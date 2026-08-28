"""Static/syntax verification for the external Cloud Run operator boundary."""

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "ops" / "cloud_run_live_proof.sh"


class CloudRunOperatorTests(unittest.TestCase):
    def test_script_is_valid_bash(self) -> None:
        result = subprocess.run(
            ["bash", "-n", str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_operator_encodes_single_writer_invariants(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("--scaling=1", text)
        self.assertIn("--concurrency=1", text)
        self.assertIn("--service-account=", text)
        self.assertIn("--build-service-account=", text)
        self.assertIn("MIRA_BEARER_TOKEN=", text)
        self.assertIn('scaling.get("scalingMode") != "MANUAL"', text)
        self.assertIn('scaling.get("manualInstanceCount") != 1', text)
        self.assertIn('template.get("maxInstanceRequestConcurrency") != 1', text)
        self.assertIn('any(item.get("tag") for item in traffic)', text)
        self.assertNotIn("--tag=", text)
        self.assertNotIn("--max-instances", text)

    def test_operator_uses_documented_bounded_source_deploy_roles(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("mira-m0-runtime", text)
        self.assertIn("mira-m0-builder", text)
        self.assertIn("roles/run.sourceDeveloper", text)
        self.assertIn("roles/serviceusage.serviceUsageConsumer", text)
        self.assertIn("roles/iam.serviceAccountUser", text)
        self.assertIn("roles/run.builder", text)
        self.assertNotIn("roles/editor", text.lower())
        self.assertNotIn("roles/owner", text.lower())

    def test_operator_preserves_secret_and_private_id_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("openssl rand -base64 48", text)
        self.assertIn("gcloud secrets versions add", text)
        self.assertIn("gcloud secrets versions access latest", text)
        self.assertIn("MIRA_GOOGLE_SPREADSHEET_ID", text)
        self.assertNotIn("1UYCYtNk_Nyr0SZqQjdis9qB2eruXLDnRIDWhBbRxCZU", text)
        self.assertNotIn("BEGIN PRIVATE KEY", text)
        self.assertNotIn("client_secret", text.lower())

    def test_operator_requires_independent_provider_readback_after_restart(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("LIVE_API_AND_RESTART_VERIFIED", text)
        self.assertIn("cloudrun-live-proof", text)
        self.assertIn("MIRA_PROOF_PHASE=post-restart", text)
        self.assertIn("independent Google Sheets readback", text)


if __name__ == "__main__":
    unittest.main()
