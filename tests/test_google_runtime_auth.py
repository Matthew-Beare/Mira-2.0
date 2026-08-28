"""Tests for Cloud Run metadata service-identity access tokens."""

import unittest

from mira.google_runtime_auth import (
    GoogleMetadataAccessTokenProvider,
    GoogleRuntimeAuthError,
)


class MutableClock:
    def __init__(self, value=1000.0):
        self.value = value

    def __call__(self):
        return self.value


class GoogleMetadataAccessTokenProviderTests(unittest.TestCase):
    def test_token_is_cached_until_refresh_skew_then_refetched(self):
        clock = MutableClock()
        responses = iter(
            (
                {"access_token": "token-one", "expires_in": 120, "token_type": "Bearer"},
                {"access_token": "token-two", "expires_in": 120, "token_type": "Bearer"},
            )
        )
        calls = []

        def fetch():
            calls.append(clock.value)
            return next(responses)

        provider = GoogleMetadataAccessTokenProvider(
            clock=clock,
            fetch_json=fetch,
            refresh_skew_seconds=30,
        )
        self.assertEqual(provider(), "token-one")
        clock.value = 1089
        self.assertEqual(provider(), "token-one")
        self.assertEqual(len(calls), 1)

        clock.value = 1090
        self.assertEqual(provider(), "token-two")
        self.assertEqual(len(calls), 2)

    def test_invalid_metadata_payloads_fail_closed(self):
        bad_payloads = (
            {},
            {"access_token": "", "expires_in": 120, "token_type": "Bearer"},
            {"access_token": "token", "expires_in": 0, "token_type": "Bearer"},
            {"access_token": "token", "expires_in": True, "token_type": "Bearer"},
            {"access_token": "token", "expires_in": 120, "token_type": "Basic"},
            ["not", "an", "object"],
        )
        for payload in bad_payloads:
            with self.subTest(payload=payload):
                provider = GoogleMetadataAccessTokenProvider(
                    fetch_json=lambda payload=payload: payload
                )
                with self.assertRaises(GoogleRuntimeAuthError):
                    provider()

    def test_invalid_refresh_skew_or_clock_fails(self):
        with self.assertRaises(GoogleRuntimeAuthError):
            GoogleMetadataAccessTokenProvider(refresh_skew_seconds=301)

        provider = GoogleMetadataAccessTokenProvider(
            clock=lambda: -1,
            fetch_json=lambda: {
                "access_token": "token",
                "expires_in": 120,
                "token_type": "Bearer",
            },
        )
        with self.assertRaises(GoogleRuntimeAuthError):
            provider()


if __name__ == "__main__":
    unittest.main()
