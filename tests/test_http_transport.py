"""Deterministic tests for scoped sessions and the WSGI API boundary."""

from io import BytesIO
import hashlib
import json
import unittest

from mira.api_core import (
    ApiService,
    AuthenticatedPrincipal,
    Grant,
    InMemoryAuditSink,
)
from mira.authority import AuthorityRegistry, AuthoritySpec
from mira.http_transport import (
    InMemorySessionStore,
    SessionAuthenticationError,
    WsgiApiApp,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class MutableClock:
    def __init__(self, value=1000):
        self.value = value

    def __call__(self):
        return self.value


class CountingService:
    def __init__(self):
        self.calls = 0

    def execute_query(self, principal, envelope):
        self.calls += 1
        raise AssertionError("service should not have been called")

    def execute_command(self, principal, envelope):
        self.calls += 1
        raise AssertionError("service should not have been called")


class HttpTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = MutableClock()
        self.tokens = iter(("T" * 43, "U" * 43, "V" * 43, "W" * 43))
        self.session_ids = iter(("session-001", "session-002", "session-003", "session-004"))
        self.sessions = InMemorySessionStore(
            clock=self.clock,
            token_factory=lambda: next(self.tokens),
            session_id_factory=lambda: next(self.session_ids),
        )

        registry_store = InMemoryStructuredStateAdapter(
            schema_version="registry-1",
            resource_types=("authority", "authority_binding"),
            event_types=("registered", "activated"),
        )
        self.registry = AuthorityRegistry(registry_store)
        self.data = InMemoryStructuredStateAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created", "updated"),
        )
        self.registry.register_authority(
            AuthoritySpec(
                authority_id="auth-primary",
                adapter_key="memory-primary",
                resource_ref="synthetic-primary",
                namespace="mira2-test",
                failure_domain="process-a",
                owner_id="user-001",
                schema_version="data-1",
                verified=True,
            ),
            idempotency_key="register-authority",
            expected_revision=0,
        )
        self.registry.register_runtime_adapter("memory-primary", self.data)
        self.registry.activate(
            "entity",
            "auth-primary",
            idempotency_key="bind-entity",
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
            client_id="client-001",
            grants=(
                Grant("entity", "read", "*"),
                Grant("entity", "query", "*"),
                Grant("entity", "upsert", "*"),
                Grant("entity", "append_event", "*"),
            ),
        )
        self.credential = self.sessions.issue(self.principal, ttl_seconds=300)
        self.app = WsgiApiApp(self.service, self.sessions, require_https=True)

    def call(
        self,
        app,
        method,
        path,
        *,
        body=None,
        raw_body=None,
        token=None,
        scheme="https",
        content_length=None,
    ):
        if raw_body is None:
            raw = b"" if body is None else json.dumps(body).encode("utf-8")
        else:
            raw = raw_body
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "wsgi.url_scheme": scheme,
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": str(len(raw)) if content_length is None else content_length,
        }
        if token is not None:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        response = b"".join(app(environ, start_response))
        parsed = json.loads(response.decode("utf-8"))
        return int(captured["status"].split()[0]), captured["headers"], parsed

    def command_body(self, **overrides):
        body = {
            "command_id": "cmd-001",
            "subject_id": "user-001",
            "data_class": "entity",
            "action": "upsert",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "entity-001",
            "payload": {"name": "Alpha"},
            "idempotency_key": "idem-001",
            "expected_revision": 0,
        }
        body.update(overrides)
        return body

    def read_body(self, **overrides):
        body = {
            "request_id": "qry-001",
            "subject_id": "user-001",
            "data_class": "entity",
            "action": "read",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "entity-001",
        }
        body.update(overrides)
        return body

    def test_issue_retains_only_token_hash_and_auth_restores_exact_principal(self) -> None:
        metadata = self.sessions.metadata(self.credential.session_id)
        self.assertEqual(
            metadata.token_hash,
            hashlib.sha256(self.credential.token.encode("utf-8")).hexdigest(),
        )
        self.assertFalse(hasattr(metadata, "token"))
        self.assertNotIn(self.credential.token, repr(self.sessions._sessions))
        self.assertEqual(self.sessions.authenticate(self.credential.token), self.principal)
        self.assertEqual(metadata.issued_at, 1000)
        self.assertEqual(metadata.expires_at, 1300)

    def test_expired_and_revoked_sessions_fail_authentication(self) -> None:
        self.clock.value = self.credential.expires_at
        with self.assertRaises(SessionAuthenticationError):
            self.sessions.authenticate(self.credential.token)

        self.clock.value = 1100
        other = self.sessions.issue(self.principal, ttl_seconds=300)
        revoked = self.sessions.revoke(other.session_id)
        self.assertEqual(revoked.revoked_at, 1100)
        with self.assertRaises(SessionAuthenticationError):
            self.sessions.authenticate(other.token)
        with self.assertRaises(SessionAuthenticationError):
            self.sessions.authenticate("Z" * 43)

    def test_health_is_nonsecret_and_does_not_require_auth(self) -> None:
        status, headers, body = self.call(self.app, "GET", "/v1/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"service": "mira", "status": "ok"})
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_missing_or_malformed_bearer_never_calls_service(self) -> None:
        service = CountingService()
        app = WsgiApiApp(service, self.sessions, require_https=True)
        status, headers, body = self.call(app, "POST", "/v1/query", body={})
        self.assertEqual(status, 401)
        self.assertEqual(body["error"]["code"], "authentication_error")
        self.assertEqual(headers["WWW-Authenticate"], "Bearer")
        self.assertEqual(service.calls, 0)

        status, _, body = self.call(
            app,
            "POST",
            "/v1/query",
            body={},
            token="not-the-real-token",
        )
        self.assertEqual(status, 401)
        self.assertEqual(service.calls, 0)

    def test_https_gate_runs_before_authentication_or_service(self) -> None:
        service = CountingService()
        app = WsgiApiApp(service, self.sessions, require_https=True)
        status, _, body = self.call(
            app,
            "POST",
            "/v1/query",
            body={},
            scheme="http",
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "https_required")
        self.assertEqual(service.calls, 0)

    def test_command_and_query_success_serialize_exact_readback(self) -> None:
        status, _, command = self.call(
            self.app,
            "POST",
            "/v1/commands",
            body=self.command_body(),
            token=self.credential.token,
        )
        self.assertEqual(status, 200)
        self.assertTrue(command["readback_verified"])
        self.assertFalse(command["idempotent_replay"])
        self.assertEqual(command["authority_id"], "auth-primary")
        self.assertEqual(command["record"]["resource_id"], "entity-001")
        self.assertEqual(command["record"]["payload"], {"name": "Alpha"})

        status, _, query = self.call(
            self.app,
            "POST",
            "/v1/query",
            body=self.read_body(),
            token=self.credential.token,
        )
        self.assertEqual(status, 200)
        self.assertEqual(query["authority_id"], "auth-primary")
        self.assertEqual(query["items"][0], command["record"])

    def test_authorization_conflict_not_found_and_validation_status_mapping(self) -> None:
        narrow = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="client-narrow",
            grants=(Grant("entity", "read", "entity-allowed"),),
        )
        narrow_credential = self.sessions.issue(narrow, ttl_seconds=300)
        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/query",
            body=self.read_body(resource_id="entity-denied"),
            token=narrow_credential.token,
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["code"], "authorization_error")

        status, _, _ = self.call(
            self.app,
            "POST",
            "/v1/commands",
            body=self.command_body(),
            token=self.credential.token,
        )
        self.assertEqual(status, 200)
        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/commands",
            body=self.command_body(
                command_id="cmd-stale",
                payload={"name": "Stale"},
                idempotency_key="stale-key",
                expected_revision=0,
            ),
            token=self.credential.token,
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"]["code"], "conflict")

        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/query",
            body=self.read_body(resource_id="entity-missing", request_id="qry-missing"),
            token=self.credential.token,
        )
        self.assertEqual(status, 404)
        self.assertEqual(body["error"]["code"], "not_found")

        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/commands",
            body=self.command_body(
                command_id="cmd-invalid",
                action="delete",
                idempotency_key="invalid-key",
            ),
            token=self.credential.token,
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "validation_error")

    def test_compatibility_maps_to_409(self) -> None:
        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/commands",
            body=self.command_body(api_major=2, idempotency_key="version-key"),
            token=self.credential.token,
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"]["code"], "compatibility_error")
        self.assertEqual(self.data.query("entity"), ())

    def test_body_bounds_json_route_and_method_fail_explicitly(self) -> None:
        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/query",
            raw_body=b"{bad-json",
            token=self.credential.token,
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "invalid_json")

        small_app = WsgiApiApp(
            self.service,
            self.sessions,
            require_https=True,
            max_body_bytes=10,
        )
        status, _, body = self.call(
            small_app,
            "POST",
            "/v1/query",
            raw_body=b"x" * 11,
            token=self.credential.token,
        )
        self.assertEqual(status, 413)
        self.assertEqual(body["error"]["code"], "payload_too_large")

        status, _, body = self.call(self.app, "GET", "/v1/query")
        self.assertEqual(status, 405)
        self.assertEqual(body["error"]["code"], "method_not_allowed")

        status, _, body = self.call(self.app, "GET", "/v1/nope")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"]["code"], "route_not_found")

    def test_transport_does_not_expand_session_grants(self) -> None:
        principal = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="client-read-only",
            grants=(Grant("entity", "read", "entity-001"),),
        )
        credential = self.sessions.issue(principal, ttl_seconds=300)
        self.assertEqual(self.sessions.authenticate(credential.token), principal)
        status, _, body = self.call(
            self.app,
            "POST",
            "/v1/commands",
            body=self.command_body(),
            token=credential.token,
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["code"], "authorization_error")


if __name__ == "__main__":
    unittest.main()
