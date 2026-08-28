"""Tests for the Cloud Run deployment composition boundary."""

from io import BytesIO, StringIO
import importlib
import json
import sys
import unittest
from unittest.mock import patch

from mira.api_core import AuditEvent, InMemoryAuditSink
from mira.cloud_run import (
    CloudRunConfigurationError,
    CloudRunHttpsProxyApp,
    FixedWindowRateLimitApp,
    JsonLineAuditSink,
    build_cloud_run_application,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class CaptureGateway:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class CloudRunTests(unittest.TestCase):
    def setUp(self):
        self.secret = "C" * 48
        self.env = {
            "MIRA_GOOGLE_SPREADSHEET_ID": "synthetic-runtime-sheet",
            "MIRA_BEARER_TOKEN": self.secret,
            "MIRA_RATE_LIMIT_PER_MINUTE": "120",
        }
        self.state = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=("authority", "authority_binding", "entity"),
            event_types=("created", "updated"),
        )
        self.audit = InMemoryAuditSink()

    def build(self, environ=None):
        captured = {}

        def gateway_factory(**kwargs):
            captured.update(kwargs)
            return CaptureGateway(**kwargs)

        def state_factory(gateway):
            self.assertIsInstance(gateway, CaptureGateway)
            return self.state

        result = build_cloud_run_application(
            self.env if environ is None else environ,
            access_token_provider=lambda: "google-runtime-token",
            audit_sink=self.audit,
            gateway_factory=gateway_factory,
            state_factory=state_factory,
        )
        return result, captured

    def call(self, app, method, path, *, body=None, token=None, forwarded_proto=None):
        raw = b"" if body is None else json.dumps(body).encode("utf-8")
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "wsgi.url_scheme": "http",
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": str(len(raw)),
        }
        if token is not None:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        if forwarded_proto is not None:
            environ["HTTP_X_FORWARDED_PROTO"] = forwarded_proto
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        response = b"".join(app(environ, start_response))
        return (
            int(captured["status"].split()[0]),
            captured["headers"],
            json.loads(response.decode("utf-8")),
        )

    def test_build_uses_runtime_only_provider_configuration_and_bootstraps(self):
        result, captured = self.build()
        self.assertEqual(result.config.spreadsheet_id, "synthetic-runtime-sheet")
        self.assertEqual(captured["spreadsheet_id"], "synthetic-runtime-sheet")
        self.assertEqual(captured["access_token_provider"](), "google-runtime-token")
        self.assertEqual(
            result.runtime.registry.resolve("entity").authority.spec.authority_id,
            "google-sheets-m0",
        )
        self.assertNotIn(self.secret, repr(result))
        self.assertNotIn(self.secret, repr(result.runtime))

    def test_proxy_https_signal_allows_protected_roundtrip_but_missing_signal_fails(self):
        result, _ = self.build()
        command = {
            "command_id": "cloud-cmd-001",
            "subject_id": "m0-synthetic-user",
            "data_class": "entity",
            "action": "upsert",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "cloud-entity-001",
            "payload": {"name": "Cloud Alpha"},
            "idempotency_key": "cloud-idem-001",
            "expected_revision": 0,
        }
        status, _, payload = self.call(
            result.app,
            "POST",
            "/v1/commands",
            body=command,
            token=self.secret,
            forwarded_proto="https",
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["readback_verified"])

        query = {
            "request_id": "cloud-qry-001",
            "subject_id": "m0-synthetic-user",
            "data_class": "entity",
            "action": "read",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "cloud-entity-001",
        }
        status, _, payload = self.call(
            result.app,
            "POST",
            "/v1/query",
            body=query,
            token=self.secret,
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "https_required")

        status, _, payload = self.call(
            result.app,
            "POST",
            "/v1/query",
            body=query,
            token=self.secret,
            forwarded_proto="https",
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["items"][0]["payload"], {"name": "Cloud Alpha"})

    def test_environment_validation_fails_closed(self):
        for missing in ("MIRA_GOOGLE_SPREADSHEET_ID", "MIRA_BEARER_TOKEN"):
            env = dict(self.env)
            del env[missing]
            with self.subTest(missing=missing):
                with self.assertRaises(CloudRunConfigurationError):
                    self.build(env)

        env = dict(self.env)
        env["MIRA_RATE_LIMIT_PER_MINUTE"] = "0"
        with self.assertRaises(CloudRunConfigurationError):
            self.build(env)

    def test_fixed_window_rate_limit_protects_only_api_routes(self):
        calls = []

        def downstream(environ, start_response):
            calls.append(environ["PATH_INFO"])
            body = b'{"ok":true}'
            start_response(
                "200 OK",
                [
                    ("Content-Type", "application/json"),
                    ("Content-Length", str(len(body))),
                ],
            )
            return [body]

        app = FixedWindowRateLimitApp(
            downstream,
            requests_per_minute=1,
            clock=lambda: 1000,
        )
        status, _, _ = self.call(
            app,
            "POST",
            "/v1/query",
            body={},
            forwarded_proto="https",
        )
        self.assertEqual(status, 200)
        status, headers, payload = self.call(
            app,
            "POST",
            "/v1/query",
            body={},
            forwarded_proto="https",
        )
        self.assertEqual(status, 429)
        self.assertEqual(headers["Retry-After"], "60")
        self.assertEqual(payload["error"]["code"], "rate_limited")

        status, _, _ = self.call(app, "GET", "/v1/health")
        self.assertEqual(status, 200)
        self.assertEqual(calls, ["/v1/query", "/v1/health"])

    def test_proxy_adapter_only_promotes_explicit_https(self):
        schemes = []

        def downstream(environ, start_response):
            schemes.append(environ["wsgi.url_scheme"])
            body = b'{"ok":true}'
            start_response("200 OK", [("Content-Length", str(len(body)))])
            return [body]

        app = CloudRunHttpsProxyApp(downstream)
        self.call(app, "GET", "/v1/health", forwarded_proto="https")
        self.call(app, "GET", "/v1/health", forwarded_proto="http")
        self.assertEqual(schemes, ["https", "http"])

    def test_json_line_audit_sink_emits_structured_event(self):
        stream = StringIO()
        sink = JsonLineAuditSink(stream)
        event = AuditEvent(
            request_id="req-1",
            actor_id="actor-1",
            client_id="client-1",
            subject_id="actor-1",
            data_class="entity",
            action="read",
            resource_id="entity-1",
            authorization="allowed",
            outcome="succeeded",
        )
        sink.record(event)
        payload = json.loads(stream.getvalue())
        self.assertEqual(payload["mira_audit"]["request_id"], "req-1")
        self.assertEqual(payload["mira_audit"]["authorization"], "allowed")

    def test_gunicorn_entrypoint_uses_cloud_run_builder(self):
        sentinel = object()
        sys.modules.pop("mira.cloud_run_entrypoint", None)
        with patch(
            "mira.cloud_run.build_cloud_run_wsgi_app",
            return_value=sentinel,
        ) as builder:
            import mira.cloud_run_entrypoint as entrypoint

            importlib.reload(entrypoint)
            self.assertIs(entrypoint.app, sentinel)
            self.assertGreaterEqual(builder.call_count, 1)


if __name__ == "__main__":
    unittest.main()
