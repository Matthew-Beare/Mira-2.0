"""Tests for restart-stable managed bearer authentication."""

import unittest

from mira.api_core import AuthenticatedPrincipal, Grant
from mira.http_transport import SessionAuthenticationError, SessionValidationError
from mira.managed_auth import StaticSecretAuthenticator


class StaticSecretAuthenticatorTests(unittest.TestCase):
    def setUp(self):
        self.secret = "S" * 48
        self.principal = AuthenticatedPrincipal(
            actor_id="m0-synthetic-user",
            client_id="stock-chatgpt-proof",
            grants=(
                Grant("entity", "read", "*"),
                Grant("entity", "upsert", "*"),
            ),
        )

    def test_authenticator_retains_only_hash_and_survives_reconstruction(self):
        first = StaticSecretAuthenticator(self.secret, self.principal)
        second = StaticSecretAuthenticator(self.secret, self.principal)

        self.assertNotIn(self.secret, repr(first.__dict__))
        self.assertNotIn(self.secret, repr(second.__dict__))
        self.assertEqual(first.authenticate(self.secret), self.principal)
        self.assertEqual(second.authenticate(self.secret), self.principal)

    def test_wrong_or_malformed_bearer_fails(self):
        auth = StaticSecretAuthenticator(self.secret, self.principal)
        with self.assertRaises(SessionAuthenticationError):
            auth.authenticate("X" * 48)
        with self.assertRaises(SessionAuthenticationError):
            auth.authenticate(" short ")
        with self.assertRaises(SessionAuthenticationError):
            auth.authenticate("short")

    def test_constructor_rejects_weak_secret_or_invalid_principal(self):
        with self.assertRaises(SessionValidationError):
            StaticSecretAuthenticator("short", self.principal)
        with self.assertRaises(SessionValidationError):
            StaticSecretAuthenticator(
                self.secret,
                AuthenticatedPrincipal(
                    actor_id="bad actor",
                    client_id="client-1",
                    grants=(Grant("entity", "read", "*"),),
                ),
            )
        with self.assertRaises(SessionValidationError):
            StaticSecretAuthenticator(
                self.secret,
                AuthenticatedPrincipal(
                    actor_id="actor-1",
                    client_id="client-1",
                    grants=(),
                ),
            )

    def test_returned_principal_is_reconstructed(self):
        auth = StaticSecretAuthenticator(self.secret, self.principal)
        first = auth.authenticate(self.secret)
        second = auth.authenticate(self.secret)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first.grants, second.grants)


if __name__ == "__main__":
    unittest.main()
