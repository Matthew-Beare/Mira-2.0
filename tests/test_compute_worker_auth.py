from __future__ import annotations

import hashlib
import io
import json
import unittest

from mira.http_transport import (
    InMemoryWorkerSessionStore,
    WORKER_CHANNEL_AUTHENTICATED_OUTBOUND,
    WORKER_CHANNEL_MUTUAL_TLS,
    WORKER_CHANNEL_WIREGUARD,
    WorkerChannelEvidence,
    WorkerSessionAuthenticationError,
    WorkerSessionValidationError,
    WsgiApiApp,
)


NOW = 1_788_901_000
TOKEN = "synthetic-worker-token-000000000000000000000000000000000000"


class ComputeWorkerAuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = NOW
        self.session_counter = 0
        self.token_counter = 0

        def session_id() -> str:
            self.session_counter += 1
            return f"worker-session-{self.session_counter}"

        def token() -> str:
            self.token_counter += 1
            return TOKEN[:-1] + str(self.token_counter % 10)

        self.store = InMemoryWorkerSessionStore(
            clock=lambda: self.now,
            token_factory=token,
            session_id_factory=session_id,
            max_channel_age_seconds=120,
        )

    def provision(
        self,
        *,
        worker_id: str = "worker-synthetic-a",
        principal_id: str = "principal-synthetic-a",
        allowed_channels: tuple[str, ...] = (
            WORKER_CHANNEL_MUTUAL_TLS,
            WORKER_CHANNEL_AUTHENTICATED_OUTBOUND,
        ),
        ttl_seconds: int = 3600,
    ):
        return self.store.provision(
            worker_id=worker_id,
            principal_id=principal_id,
            allowed_channels=allowed_channels,
            ttl_seconds=ttl_seconds,
        )

    def channel(
        self,
        *,
        kind: str = WORKER_CHANNEL_MUTUAL_TLS,
        authenticated: bool = True,
        confidential: bool = True,
        observed_at: int | None = None,
    ) -> WorkerChannelEvidence:
        return WorkerChannelEvidence(
            channel_kind=kind,
            peer_authenticated=authenticated,
            confidential=confidential,
            observed_at=self.now - 30 if observed_at is None else observed_at,
        )

    def test_provision_stores_only_verifier_and_exact_worker_principal_binding(self) -> None:
        issued = self.provision()
        metadata = self.store.metadata(issued.session_id)

        self.assertEqual(metadata.worker_id, "worker-synthetic-a")
        self.assertEqual(metadata.principal_id, "principal-synthetic-a")
        self.assertEqual(metadata.token_hash, hashlib.sha256(issued.token.encode()).hexdigest())
        self.assertNotIn(issued.token, repr(metadata))
        self.assertFalse(hasattr(metadata, "token"))
        self.assertFalse(hasattr(metadata, "credential"))
        self.assertFalse(hasattr(metadata, "grants"))
        self.assertFalse(hasattr(metadata, "actor_id"))
        self.assertFalse(hasattr(metadata, "client_id"))
        self.assertEqual(
            metadata.allowed_channels,
            tuple(sorted((WORKER_CHANNEL_MUTUAL_TLS, WORKER_CHANNEL_AUTHENTICATED_OUTBOUND))),
        )

    def test_authentication_returns_existing_secret_free_registry_identity_evidence(self) -> None:
        issued = self.provision()
        evidence = self.store.authenticate(
            worker_id=issued.worker_id,
            token=issued.token,
            channel=self.channel(),
        )

        self.assertEqual(evidence.principal_id, issued.principal_id)
        self.assertEqual(evidence.state, "verified")
        self.assertEqual(evidence.verified_at, "2026-09-08T20:56:40Z")
        self.assertFalse(hasattr(evidence, "token"))
        self.assertFalse(hasattr(evidence, "grants"))
        self.assertFalse(hasattr(evidence, "hostname"))
        self.assertFalse(hasattr(evidence, "ip_address"))

    def test_wrong_worker_or_token_fails_closed(self) -> None:
        issued = self.provision()
        with self.assertRaises(WorkerSessionAuthenticationError):
            self.store.authenticate(
                worker_id="worker-synthetic-b",
                token=issued.token,
                channel=self.channel(),
            )
        with self.assertRaises(WorkerSessionAuthenticationError):
            self.store.authenticate(
                worker_id=issued.worker_id,
                token="x" * 48,
                channel=self.channel(),
            )

    def test_expired_and_revoked_credentials_fail_closed(self) -> None:
        issued = self.provision(ttl_seconds=60)
        self.now += 60
        with self.assertRaises(WorkerSessionAuthenticationError):
            self.store.authenticate(
                worker_id=issued.worker_id,
                token=issued.token,
                channel=self.channel(observed_at=self.now),
            )

        self.now = NOW
        issued = self.provision()
        first = self.store.revoke(issued.session_id)
        second = self.store.revoke(issued.session_id)
        self.assertEqual(first.revoked_at, second.revoked_at)
        with self.assertRaises(WorkerSessionAuthenticationError):
            self.store.authenticate(
                worker_id=issued.worker_id,
                token=issued.token,
                channel=self.channel(),
            )

    def test_channel_must_be_allowed_authenticated_and_confidential(self) -> None:
        issued = self.provision(allowed_channels=(WORKER_CHANNEL_MUTUAL_TLS,))

        for channel in (
            self.channel(kind=WORKER_CHANNEL_WIREGUARD),
            self.channel(authenticated=False),
            self.channel(confidential=False),
        ):
            with self.subTest(channel=channel):
                with self.assertRaises(WorkerSessionAuthenticationError):
                    self.store.authenticate(
                        worker_id=issued.worker_id,
                        token=issued.token,
                        channel=channel,
                    )

    def test_channel_evidence_must_be_fresh_and_not_from_future(self) -> None:
        issued = self.provision()
        with self.assertRaises(WorkerSessionAuthenticationError):
            self.store.authenticate(
                worker_id=issued.worker_id,
                token=issued.token,
                channel=self.channel(observed_at=self.now - 121),
            )
        with self.assertRaises(WorkerSessionAuthenticationError):
            self.store.authenticate(
                worker_id=issued.worker_id,
                token=issued.token,
                channel=self.channel(observed_at=self.now + 1),
            )

    def test_only_explicit_secure_channel_classes_are_accepted(self) -> None:
        with self.assertRaises(WorkerSessionValidationError):
            WorkerChannelEvidence(
                channel_kind="plain_lan",
                peer_authenticated=True,
                confidential=True,
                observed_at=self.now,
            )
        with self.assertRaises(WorkerSessionValidationError):
            self.provision(allowed_channels=("plain_lan",))
        with self.assertRaises(WorkerSessionValidationError):
            self.provision(allowed_channels=())

    def test_worker_metadata_contains_no_private_binding_or_execution_fields(self) -> None:
        issued = self.provision()
        metadata = self.store.metadata(issued.session_id)
        forbidden = {
            "hostname",
            "ip_address",
            "mac_address",
            "serial_number",
            "private_key",
            "certificate",
            "vpn_peer",
            "shell_endpoint",
            "python_endpoint",
            "inference_endpoint",
            "model_path",
            "shell_command",
            "python_code",
        }
        self.assertTrue(forbidden.isdisjoint(vars(metadata)))

    def test_existing_wsgi_surface_does_not_gain_raw_worker_execution_routes(self) -> None:
        class NeverAuthenticator:
            def authenticate(self, token: str):
                raise AssertionError("unknown route must not authenticate")

        app = WsgiApiApp(None, NeverAuthenticator())  # type: ignore[arg-type]
        for path in (
            "/v1/workers/execute",
            "/v1/inference",
            "/v1/python",
            "/v1/shell",
        ):
            with self.subTest(path=path):
                captured: list[str] = []

                def start_response(status, headers):
                    captured.append(status)

                body = b"".join(
                    app(
                        {
                            "REQUEST_METHOD": "POST",
                            "PATH_INFO": path,
                            "wsgi.url_scheme": "https",
                            "wsgi.input": io.BytesIO(b""),
                            "CONTENT_LENGTH": "0",
                        },
                        start_response,
                    )
                )
                self.assertTrue(captured[0].startswith("404 "))
                self.assertEqual(json.loads(body)["error"]["code"], "route_not_found")


if __name__ == "__main__":
    unittest.main()
