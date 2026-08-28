"""Tests for provider-neutral managed API runtime assembly."""

from dataclasses import replace
from io import BytesIO
import json
import unittest

from mira.api_core import AuthenticatedPrincipal, Grant, InMemoryAuditSink
from mira.authority import AuthorityRegistry, AuthoritySpec
from mira.http_transport import SessionAuthenticationError
from mira.runtime import RuntimeAssemblyError, RuntimeConfig, assemble_managed_runtime
from mira.structured_state import HealthStatus, InMemoryStructuredStateAdapter


class StaticAuthenticator:
    def __init__(self, token, principal):
        self._token = token
        self._principal = principal

    def authenticate(self, token):
        if token != self._token:
            raise SessionAuthenticationError("unknown bearer credential")
        return self._principal


class UnhealthyState(InMemoryStructuredStateAdapter):
    def health(self):
        schema = self.schema()
        return HealthStatus(ok=False, adapter="memory", schema_version=schema.schema_version)


class RuntimeAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.state = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=("authority", "authority_binding", "entity"),
            event_types=("created", "updated"),
        )
        self.spec = AuthoritySpec(
            authority_id="google-sheets-m0",
            adapter_key="google-sheets",
            resource_ref="runtime:google-structured-state",
            namespace="mira-2-sandbox",
            failure_domain="google-sheets-sandbox",
            owner_id="m0-synthetic-user",
            schema_version="mira-structured-state-v1",
            verified=True,
            enabled=True,
        )
        self.config = RuntimeConfig(authority=self.spec)
        self.principal = AuthenticatedPrincipal(
            actor_id="m0-synthetic-user",
            client_id="stock-chatgpt-proof",
            grants=(
                Grant("entity", "read", "*"),
                Grant("entity", "query", "*"),
                Grant("entity", "upsert", "*"),
                Grant("entity", "append_event", "*"),
            ),
        )
        self.token = "R" * 43
        self.authenticator = StaticAuthenticator(self.token, self.principal)
        self.audit = InMemoryAuditSink()

    def assemble(self, state=None, config=None):
        return assemble_managed_runtime(
            config or self.config,
            structured_state=state or self.state,
            authenticator=self.authenticator,
            audit_sink=self.audit,
        )

    def call(self, app, path, body, token=None):
        raw = json.dumps(body).encode("utf-8")
        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": path,
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": str(len(raw)),
        }
        if token is not None:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        response = b"".join(app(environ, start_response))
        return int(captured["status"].split()[0]), json.loads(response.decode("utf-8"))

    def test_assembly_bootstraps_and_resolves_entity_before_return(self):
        runtime = self.assemble()
        self.assertTrue(runtime.bootstrap.authority_created)
        self.assertTrue(runtime.bootstrap.binding_created)
        route = runtime.registry.resolve("entity")
        self.assertEqual(route.authority.spec, self.spec)
        self.assertIs(route.adapter, self.state)

    def test_assembled_wsgi_uses_injected_authenticator_for_command_and_query(self):
        runtime = self.assemble()
        command = {
            "command_id": "cmd-runtime-001",
            "subject_id": "m0-synthetic-user",
            "data_class": "entity",
            "action": "upsert",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "runtime-entity-001",
            "payload": {"name": "Runtime Alpha"},
            "idempotency_key": "runtime-idem-001",
            "expected_revision": 0,
        }
        status, result = self.call(runtime.app, "/v1/commands", command, self.token)
        self.assertEqual(status, 200)
        self.assertTrue(result["readback_verified"])
        self.assertEqual(result["record"]["payload"], {"name": "Runtime Alpha"})

        query = {
            "request_id": "qry-runtime-001",
            "subject_id": "m0-synthetic-user",
            "data_class": "entity",
            "action": "read",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "runtime-entity-001",
        }
        status, result = self.call(runtime.app, "/v1/query", query, self.token)
        self.assertEqual(status, 200)
        self.assertEqual(result["items"][0]["resource_id"], "runtime-entity-001")

        status, result = self.call(runtime.app, "/v1/query", query, "X" * 43)
        self.assertEqual(status, 401)
        self.assertEqual(result["error"]["code"], "authentication_error")

    def test_invalid_config_fails_before_runtime_creation(self):
        with self.assertRaisesRegex(RuntimeAssemblyError, "supports only data_class=entity"):
            self.assemble(config=replace(self.config, data_class="tasks"))
        with self.assertRaisesRegex(RuntimeAssemblyError, "api_major"):
            self.assemble(config=replace(self.config, api_major=0))

    def test_unhealthy_or_schema_incompatible_state_fails_closed(self):
        unhealthy = UnhealthyState(
            schema_version="mira-structured-state-v1",
            resource_types=("authority", "authority_binding", "entity"),
            event_types=("created", "updated"),
        )
        with self.assertRaisesRegex(RuntimeAssemblyError, "unhealthy"):
            self.assemble(state=unhealthy)

        wrong_schema = InMemoryStructuredStateAdapter(
            schema_version="wrong-version",
            resource_types=("authority", "authority_binding", "entity"),
            event_types=("created", "updated"),
        )
        with self.assertRaisesRegex(RuntimeAssemblyError, "does not match Authority"):
            self.assemble(state=wrong_schema)

    def test_persisted_authority_mismatch_fails_before_serving(self):
        registry = AuthorityRegistry(self.state)
        different = replace(self.spec, resource_ref="runtime:unexpected-store")
        registry.register_authority(
            different,
            idempotency_key="preexisting-authority",
            expected_revision=0,
        )

        with self.assertRaisesRegex(RuntimeAssemblyError, "startup verification failed"):
            self.assemble()

        self.assertEqual(
            registry.get_authority(self.spec.authority_id).spec.resource_ref,
            "runtime:unexpected-store",
        )
        self.assertEqual(self.state.query("authority_binding"), ())


if __name__ == "__main__":
    unittest.main()
