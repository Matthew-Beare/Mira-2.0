"""Deterministic tests for the Android-facing client session trust seam."""

import unittest

from mira.api_core import (
    ApiAuthenticationError,
    ApiAuthorizationError,
    ApiConflictError,
    AuthenticatedPrincipal,
    ClientSessionRegistry,
    Grant,
)


class ClientSessionRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.secret = "s" * 48
        self.registry = ClientSessionRegistry(lambda: self.secret)
        self.grants = (
            Grant("entity", "read", "*"),
            Grant("entity", "query", "*"),
            Grant("entity", "upsert", "entity-001"),
        )

    def test_enrollment_returns_secret_once_and_stores_only_verifier(self) -> None:
        enrollment = self.registry.enroll(
            actor_id="user-001",
            client_id="android-001",
            grants=self.grants,
        )

        self.assertEqual(enrollment.actor_id, "user-001")
        self.assertEqual(enrollment.client_id, "android-001")
        self.assertEqual(enrollment.credential, self.secret)
        self.assertEqual(enrollment.grants, self.grants)

        snapshot = self.registry.snapshot("android-001")
        self.assertEqual(snapshot.actor_id, "user-001")
        self.assertEqual(snapshot.client_id, "android-001")
        self.assertEqual(snapshot.grants, self.grants)
        self.assertFalse(snapshot.revoked)
        self.assertNotEqual(snapshot.credential_verifier, self.secret)
        self.assertNotIn(self.secret, repr(snapshot))
        self.assertEqual(len(snapshot.credential_verifier), 64)

    def test_correct_credential_reconstructs_exact_principal(self) -> None:
        self.registry.enroll(
            actor_id="user-001",
            client_id="android-001",
            grants=self.grants,
        )

        principal = self.registry.authenticate(
            client_id="android-001",
            credential=self.secret,
        )

        self.assertEqual(
            principal,
            AuthenticatedPrincipal(
                actor_id="user-001",
                client_id="android-001",
                grants=self.grants,
            ),
        )

    def test_wrong_credential_fails_closed(self) -> None:
        self.registry.enroll(
            actor_id="user-001",
            client_id="android-001",
            grants=self.grants,
        )

        with self.assertRaises(ApiAuthenticationError):
            self.registry.authenticate(
                client_id="android-001",
                credential="x" * 48,
            )

    def test_revocation_is_immediate_idempotent_and_readback_verifiable(self) -> None:
        self.registry.enroll(
            actor_id="user-001",
            client_id="android-001",
            grants=self.grants,
        )

        first = self.registry.revoke("android-001")
        second = self.registry.revoke("android-001")
        readback = self.registry.snapshot("android-001")

        self.assertTrue(first.revoked)
        self.assertEqual(first, second)
        self.assertEqual(second, readback)
        with self.assertRaises(ApiAuthenticationError):
            self.registry.authenticate(
                client_id="android-001",
                credential=self.secret,
            )

    def test_duplicate_client_identity_conflicts_without_rotating_secret(self) -> None:
        self.registry.enroll(
            actor_id="user-001",
            client_id="android-001",
            grants=self.grants,
        )
        before = self.registry.snapshot("android-001")

        with self.assertRaises(ApiConflictError):
            self.registry.enroll(
                actor_id="user-001",
                client_id="android-001",
                grants=(Grant("entity", "read", "*"),),
            )

        self.assertEqual(self.registry.snapshot("android-001"), before)

    def test_invalid_grant_cannot_be_smuggled_through_enrollment(self) -> None:
        with self.assertRaises(ApiAuthorizationError):
            self.registry.enroll(
                actor_id="user-001",
                client_id="android-001",
                grants=(Grant("entity", "query", "entity-001"),),
            )

    def test_session_identity_is_explicit_same_user_identity(self) -> None:
        self.registry.enroll(
            actor_id="user-001",
            client_id="android-001",
            grants=(Grant("entity", "read", "entity-001"),),
        )
        principal = self.registry.authenticate(
            client_id="android-001",
            credential=self.secret,
        )

        self.assertEqual(principal.actor_id, "user-001")
        self.assertNotEqual(principal.client_id, principal.actor_id)
        self.assertEqual(
            principal.grants,
            (Grant("entity", "read", "entity-001"),),
        )


if __name__ == "__main__":
    unittest.main()
