"""Tests for the maintainer-only Apps Script publication seam."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ops.publish_apps_script import (
    OAuthCredential,
    PublicationError,
    load_clasp_credential,
    load_runtime_files,
    publish_bound_runtime,
    publish_existing_runtime,
    refresh_access_token,
)


class FakeTransport:
    def __init__(
        self,
        *,
        drift: bool = False,
        wrong_parent: bool = False,
        binding_drift: bool = False,
    ) -> None:
        self.calls: list[tuple[str, str, object, str]] = []
        self.content: dict[str, object] | None = None
        self.drift = drift
        self.wrong_parent = wrong_parent
        self.binding_drift = binding_drift

    def __call__(self, method: str, path: str, body: object, token: str):
        self.calls.append((method, path, body, token))
        if method == "POST" and path == "/projects":
            assert isinstance(body, dict)
            return {
                "scriptId": "script_project_1234567890",
                "parentId": (
                    "other_sheet_1234567890" if self.wrong_parent else body["parentId"]
                ),
            }
        if method == "GET" and path == "/projects/script_project_1234567890":
            return {
                "scriptId": "script_project_1234567890",
                "parentId": (
                    "other_sheet_1234567890"
                    if self.binding_drift
                    else "sheet_parent_1234567890"
                ),
            }
        if method == "PUT" and path.endswith("/content"):
            assert isinstance(body, dict)
            self.content = json.loads(json.dumps(body))
            return self.content
        if method == "GET" and path.endswith("/content"):
            assert self.content is not None
            content = json.loads(json.dumps(self.content))
            if self.drift:
                content["files"][0]["source"] += "\n// provider drift"
            return content
        raise AssertionError(f"unexpected fake request: {method} {path}")


class AppsScriptPublicationTests(unittest.TestCase):
    def test_runtime_bundle_is_minimal_and_manifest_is_canonicalized(self) -> None:
        files = load_runtime_files()
        self.assertEqual(
            [(item.name, item.type) for item in files],
            [
                ("Code", "SERVER_JS"),
                ("CommandWorker", "SERVER_JS"),
                ("appsscript", "JSON"),
            ],
        )
        manifest = next(item for item in files if item.name == "appsscript")
        self.assertEqual(
            manifest.source,
            json.dumps(
                json.loads(manifest.source),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
        )
        self.assertNotIn("MIRA_NO_APP_INSTRUCTIONS", "\n".join(item.name for item in files))
        self.assertNotIn("GoogleCalendarProjection", "\n".join(item.name for item in files))

    def test_publish_creates_reads_binding_updates_head_and_exact_reads_back(self) -> None:
        transport = FakeTransport()
        result = publish_bound_runtime(
            sheet_id="sheet_parent_1234567890",
            access_token="short-lived-token",
            transport=transport,
        )
        self.assertEqual(result.parent_id, "sheet_parent_1234567890")
        self.assertEqual(result.script_id, "script_project_1234567890")
        self.assertEqual(
            [call[:2] for call in transport.calls],
            [
                ("POST", "/projects"),
                ("GET", "/projects/script_project_1234567890"),
                ("PUT", "/projects/script_project_1234567890/content"),
                ("GET", "/projects/script_project_1234567890/content"),
            ],
        )
        create_body = transport.calls[0][2]
        self.assertEqual(create_body["parentId"], "sheet_parent_1234567890")
        self.assertTrue(all(call[3] == "short-lived-token" for call in transport.calls))

    def test_existing_project_is_parent_verified_before_any_update(self) -> None:
        transport = FakeTransport()
        result = publish_existing_runtime(
            sheet_id="sheet_parent_1234567890",
            script_id="script_project_1234567890",
            access_token="short-lived-token",
            transport=transport,
        )
        self.assertEqual(result.script_id, "script_project_1234567890")
        self.assertEqual(
            [call[:2] for call in transport.calls],
            [
                ("GET", "/projects/script_project_1234567890"),
                ("PUT", "/projects/script_project_1234567890/content"),
                ("GET", "/projects/script_project_1234567890/content"),
            ],
        )

    def test_provider_readback_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(PublicationError, "provider readback"):
            publish_bound_runtime(
                sheet_id="sheet_parent_1234567890",
                access_token="short-lived-token",
                transport=FakeTransport(drift=True),
            )

    def test_wrong_parent_create_response_fails_before_metadata_or_content(self) -> None:
        transport = FakeTransport(wrong_parent=True)
        with self.assertRaisesRegex(PublicationError, "not bound"):
            publish_bound_runtime(
                sheet_id="sheet_parent_1234567890",
                access_token="short-lived-token",
                transport=transport,
            )
        self.assertEqual(len(transport.calls), 1)

    def test_independent_binding_drift_fails_before_content_update(self) -> None:
        transport = FakeTransport(binding_drift=True)
        with self.assertRaisesRegex(PublicationError, "binding readback"):
            publish_bound_runtime(
                sheet_id="sheet_parent_1234567890",
                access_token="short-lived-token",
                transport=transport,
            )
        self.assertEqual(
            [call[:2] for call in transport.calls],
            [
                ("POST", "/projects"),
                ("GET", "/projects/script_project_1234567890"),
            ],
        )

    def test_current_clasp_v3_credential_is_loaded_without_echoing_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".clasprc.json"
            path.write_text(
                json.dumps(
                    {
                        "tokens": {
                            "default": {
                                "type": "authorized_user",
                                "client_id": "client-id.apps.googleusercontent.com",
                                "client_secret": "private-client-secret",
                                "refresh_token": "private-refresh-token",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            credential = load_clasp_credential(path)
        self.assertEqual(credential.client_id, "client-id.apps.googleusercontent.com")
        self.assertEqual(credential.client_secret, "private-client-secret")
        self.assertEqual(credential.refresh_token, "private-refresh-token")

    def test_legacy_local_clasp_credential_is_supported_for_migration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".clasprc.json"
            path.write_text(
                json.dumps(
                    {
                        "oauth2ClientSettings": {
                            "clientId": "legacy-client-id",
                            "clientSecret": "legacy-client-secret",
                        },
                        "token": {"refresh_token": "legacy-refresh-token"},
                    }
                ),
                encoding="utf-8",
            )
            credential = load_clasp_credential(path)
        self.assertEqual(
            credential,
            OAuthCredential(
                client_id="legacy-client-id",
                client_secret="legacy-client-secret",
                refresh_token="legacy-refresh-token",
            ),
        )

    def test_refresh_uses_only_refresh_grant_and_returns_ephemeral_access_token(self) -> None:
        observed: list[dict[str, str]] = []

        def token_transport(form):
            observed.append(dict(form))
            return {"access_token": "ephemeral-access-token", "expires_in": 3600}

        token = refresh_access_token(
            OAuthCredential(
                client_id="client-id",
                client_secret="client-secret",
                refresh_token="refresh-token",
            ),
            transport=token_transport,
        )
        self.assertEqual(token, "ephemeral-access-token")
        self.assertEqual(
            observed,
            [
                {
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                    "refresh_token": "refresh-token",
                    "grant_type": "refresh_token",
                }
            ],
        )

    def test_refresh_allows_public_client_without_client_secret(self) -> None:
        def token_transport(form):
            self.assertNotIn("client_secret", form)
            return {"access_token": "ephemeral-access-token"}

        self.assertEqual(
            refresh_access_token(
                OAuthCredential(
                    client_id="client-id",
                    client_secret=None,
                    refresh_token="refresh-token",
                ),
                transport=token_transport,
            ),
            "ephemeral-access-token",
        )

    def test_missing_refresh_material_fails_without_disclosing_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".clasprc.json"
            path.write_text(
                json.dumps(
                    {
                        "tokens": {
                            "default": {
                                "client_id": "client-id",
                                "access_token": "should-never-appear",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PublicationError, "missing refresh_token") as caught:
                load_clasp_credential(path)
        self.assertNotIn("should-never-appear", str(caught.exception))

    def test_missing_or_invalid_runtime_material_fails_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "workspace" / "apps_script"
            runtime.mkdir(parents=True)
            (runtime / "Code.gs").write_text("function onOpen() {}", encoding="utf-8")
            (runtime / "CommandWorker.gs").write_text("function worker() {}", encoding="utf-8")
            (runtime / "appsscript.json").write_text("not-json", encoding="utf-8")
            with self.assertRaisesRegex(PublicationError, "valid JSON"):
                load_runtime_files(root)

    def test_invalid_sheet_id_fails_before_transport(self) -> None:
        transport = FakeTransport()
        with self.assertRaisesRegex(PublicationError, "sheet_id is invalid"):
            publish_bound_runtime(
                sheet_id="bad id",
                access_token="short-lived-token",
                transport=transport,
            )
        self.assertEqual(transport.calls, [])


if __name__ == "__main__":
    unittest.main()
