"""End-to-end synthetic proof across every merged MIRA core layer."""

from dataclasses import asdict
from io import BytesIO
import json
import unittest

from mira.api_core import ApiService, AuthenticatedPrincipal, Grant, InMemoryAuditSink
from mira.authority import AuthorityRegistry, AuthoritySpec
from mira.http_transport import InMemorySessionStore, WsgiApiApp
from mira.structured_state import InMemoryStructuredStateAdapter


class SyntheticRoundtripIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_store = InMemoryStructuredStateAdapter(
            schema_version="registry-1",
            resource_types=("authority", "authority_binding"),
            event_types=("registered", "activated"),
        )
        self.canonical_store = InMemoryStructuredStateAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created", "updated"),
        )
        self.assertIsNot(self.registry_store, self.canonical_store)

        self.registry = AuthorityRegistry(self.registry_store)
        self.registry.register_authority(
            AuthoritySpec(
                authority_id="auth-synthetic-entity",
                adapter_key="synthetic-entity-store",
                resource_ref="memory://canonical-entity-store",
                namespace="mira2-synthetic",
                failure_domain="synthetic-process",
                owner_id="user-001",
                schema_version="data-1",
                verified=True,
            ),
            idempotency_key="register-auth-synthetic",
            expected_revision=0,
        )
        self.registry.register_runtime_adapter(
            "synthetic-entity-store",
            self.canonical_store,
        )
        self.registry.activate(
            "entity",
            "auth-synthetic-entity",
            idempotency_key="bind-entity-synthetic",
            expected_revision=0,
        )

        self.audit = InMemoryAuditSink()
        self.service = ApiService(
            self.registry,
            self.audit,
            api_major=1,
            schema_version="mira-api-1",
        )
        self.principal = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="synthetic-client-001",
            grants=(
                Grant("entity", "read", "*"),
                Grant("entity", "query", "*"),
                Grant("entity", "upsert", "*"),
            ),
        )
        self.sessions = InMemorySessionStore(
            clock=lambda: 1000,
            token_factory=lambda: "S" * 43,
            session_id_factory=lambda: "session-synthetic-001",
        )
        self.credential = self.sessions.issue(self.principal, ttl_seconds=3600)
        self.app = WsgiApiApp(self.service, self.sessions, require_https=True)

    def request(self, path, body, *, token=True):
        raw = json.dumps(body).encode("utf-8")
        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": path,
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": str(len(raw)),
        }
        if token is True:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {self.credential.token}"
        elif isinstance(token, str):
            environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        response = b"".join(self.app(environ, start_response))
        return int(captured["status"].split()[0]), json.loads(response.decode("utf-8"))

    def command(self, *, command_id, name, key, expected_revision):
        return {
            "command_id": command_id,
            "subject_id": "user-001",
            "data_class": "entity",
            "action": "upsert",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "entity-001",
            "payload": {"name": name},
            "idempotency_key": key,
            "expected_revision": expected_revision,
        }

    def read_query(self, request_id):
        return {
            "request_id": request_id,
            "subject_id": "user-001",
            "data_class": "entity",
            "action": "read",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "entity-001",
        }

    def test_full_create_read_update_replay_conflict_and_exact_readback(self) -> None:
        create_body = self.command(
            command_id="cmd-create",
            name="Alpha",
            key="idem-create",
            expected_revision=0,
        )

        status, denied = self.request("/v1/commands", create_body, token=False)
        self.assertEqual(status, 401)
        self.assertEqual(denied["error"]["code"], "authentication_error")
        self.assertEqual(self.canonical_store.query("entity"), ())
        self.assertEqual(self.audit.events(), ())

        status, created = self.request("/v1/commands", create_body)
        self.assertEqual(status, 200)
        self.assertTrue(created["readback_verified"])
        self.assertFalse(created["idempotent_replay"])
        self.assertEqual(created["authority_id"], "auth-synthetic-entity")
        self.assertEqual(created["record"]["revision"], 1)
        self.assertEqual(created["record"]["payload"], {"name": "Alpha"})

        status, read_alpha = self.request("/v1/query", self.read_query("qry-alpha"))
        self.assertEqual(status, 200)
        self.assertEqual(read_alpha["items"], [created["record"]])

        update_body = self.command(
            command_id="cmd-update",
            name="Beta",
            key="idem-update",
            expected_revision=1,
        )
        status, updated = self.request("/v1/commands", update_body)
        self.assertEqual(status, 200)
        self.assertFalse(updated["idempotent_replay"])
        self.assertTrue(updated["readback_verified"])
        self.assertEqual(updated["record"]["revision"], 2)
        self.assertEqual(updated["record"]["payload"], {"name": "Beta"})

        status, replayed = self.request("/v1/commands", update_body)
        self.assertEqual(status, 200)
        self.assertTrue(replayed["idempotent_replay"])
        self.assertEqual(replayed["record"], updated["record"])
        self.assertEqual(self.canonical_store.get("entity", "entity-001").revision, 2)

        conflicting_reuse = self.command(
            command_id="cmd-update-different",
            name="Gamma",
            key="idem-update",
            expected_revision=1,
        )
        status, conflict = self.request("/v1/commands", conflicting_reuse)
        self.assertEqual(status, 409)
        self.assertEqual(conflict["error"]["code"], "conflict")
        self.assertEqual(self.canonical_store.get("entity", "entity-001").payload, {"name": "Beta"})
        self.assertEqual(self.canonical_store.get("entity", "entity-001").revision, 2)

        stale = self.command(
            command_id="cmd-stale",
            name="Delta",
            key="idem-stale",
            expected_revision=1,
        )
        status, stale_response = self.request("/v1/commands", stale)
        self.assertEqual(status, 409)
        self.assertEqual(stale_response["error"]["code"], "conflict")
        self.assertEqual(self.canonical_store.get("entity", "entity-001").payload, {"name": "Beta"})
        self.assertEqual(self.canonical_store.get("entity", "entity-001").revision, 2)

        status, final_http = self.request("/v1/query", self.read_query("qry-final"))
        self.assertEqual(status, 200)
        direct = self.canonical_store.get("entity", "entity-001")
        self.assertEqual(final_http["items"], [asdict(direct)])
        self.assertEqual(final_http["items"][0], updated["record"])

        events = self.audit.events()
        successful_updates = [
            event
            for event in events
            if event.action == "upsert" and event.outcome == "success"
        ]
        failed_updates = [
            event
            for event in events
            if event.action == "upsert" and event.outcome == "failed"
        ]
        self.assertEqual(len(successful_updates), 3)  # create, update, replay
        self.assertEqual(len(failed_updates), 2)  # changed replay key + stale revision
        for event in successful_updates + failed_updates:
            self.assertEqual(event.actor_id, "user-001")
            self.assertEqual(event.client_id, "synthetic-client-001")
            self.assertEqual(event.resource_id, "entity-001")
            self.assertEqual(event.authority_id, "auth-synthetic-entity")
        self.assertTrue(all(event.authorization == "allowed" for event in events))
        self.assertTrue(all(event.error_code == "conflict" for event in failed_updates))

    def test_invalid_bearer_never_creates_second_client_side_truth(self) -> None:
        body = self.command(
            command_id="cmd-invalid-auth",
            name="Unauthorized",
            key="idem-invalid-auth",
            expected_revision=0,
        )
        status, response = self.request("/v1/commands", body, token="X" * 43)
        self.assertEqual(status, 401)
        self.assertEqual(response["error"]["code"], "authentication_error")
        self.assertEqual(self.canonical_store.query("entity"), ())
        self.assertEqual(self.audit.events(), ())


if __name__ == "__main__":
    unittest.main()
