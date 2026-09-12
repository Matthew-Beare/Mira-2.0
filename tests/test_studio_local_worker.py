from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from ops.studio_local_worker import (
    StudioWorkerError,
    WorkerManifest,
    run_manifest,
)


DRAFT_ID = "intake-" + ("a" * 64)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        shell=False,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


class FakeModelServer:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.requests: list[dict] = []

        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802 - stdlib callback name
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                owner.requests.append(json.loads(raw.decode("utf-8")))
                if not owner.responses:
                    self.send_response(500)
                    self.end_headers()
                    return
                content = owner.responses.pop(0)
                encoded = json.dumps(
                    {"choices": [{"message": {"content": content}}]}
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, format, *args):  # noqa: A002
                return

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.httpd.server_port}/v1"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)


class StudioLocalWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo / "check.py").write_text(
            "from pathlib import Path\n"
            "text = Path('app.py').read_text(encoding='utf-8')\n"
            "raise SystemExit(0 if 'VALUE = 2' in text else 1)\n",
            encoding="utf-8",
        )
        git(self.repo, "add", "app.py", "check.py")
        git(
            self.repo,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-q",
            "-m",
            "base",
        )
        self.base_sha = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def manifest(
        self,
        base_url: str,
        *,
        branch: str = "studio/test-change",
        max_rounds: int = 3,
        test_argv: tuple[str, ...] | None = None,
        allowed_paths: tuple[str, ...] = ("app.py",),
    ) -> WorkerManifest:
        return WorkerManifest(
            draft_id=DRAFT_ID,
            objective="Change the application value to two without touching tests.",
            repo_path=str(self.repo),
            base_sha=self.base_sha,
            branch_name=branch,
            allowed_paths=allowed_paths,
            test_argv=test_argv or (sys.executable, "check.py"),
            model_base_url=base_url,
            model="synthetic-local-model",
            max_rounds=max_rounds,
            wall_timeout_seconds=30,
            test_timeout_seconds=10,
            model_timeout_seconds=10,
        )

    def response(self, value: int, *, path: str = "app.py") -> str:
        return json.dumps(
            {
                "files": [{"path": path, "content": f"VALUE = {value}\n"}],
                "summary": f"Set value to {value}",
            },
            sort_keys=True,
        )

    def test_end_to_end_real_git_branch_model_call_and_test(self):
        with FakeModelServer([self.response(2)]) as model:
            result = run_manifest(self.manifest(model.base_url))

        self.assertEqual(result.status, "ready_for_review")
        self.assertEqual(result.stop_reason, "tests_passed")
        self.assertFalse(result.baseline_test.passed)
        self.assertEqual(len(result.rounds), 1)
        self.assertTrue(result.rounds[0].test.passed)
        self.assertEqual(result.rounds[0].changed_paths, ("app.py",))
        self.assertEqual(len(model.requests), 1)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.base_sha)
        self.assertEqual(
            (self.repo / "app.py").read_text(encoding="utf-8"), "VALUE = 1\n"
        )

        worktree = Path(result.worktree_path)
        self.assertEqual(worktree.joinpath("app.py").read_text(encoding="utf-8"), "VALUE = 2\n")
        self.assertEqual(git(worktree, "rev-parse", "HEAD"), result.final_candidate_sha)
        self.assertEqual(
            git(self.repo, "rev-parse", "refs/heads/studio/test-change"),
            result.final_candidate_sha,
        )
        self.assertTrue(Path(result.evidence_path, "baseline.json").is_file())
        self.assertTrue(Path(result.evidence_path, "round-01.json").is_file())
        self.assertTrue(Path(result.evidence_path, "result.json").is_file())

    def test_non_loopback_model_endpoint_is_rejected_before_execution(self):
        manifest = self.manifest("https://example.com/v1")
        with self.assertRaisesRegex(StudioWorkerError, "loopback"):
            manifest.validate()
        self.assertNotIn("studio/test-change", git(self.repo, "branch", "--list"))

    def test_manifest_rejects_path_traversal_and_noncanonical_allowlist(self):
        for paths in (
            ("../escape.py",),
            ("/tmp/escape.py",),
            ("app.py", "app.py"),
            ("z.py", "app.py"),
            (".git/config",),
        ):
            with self.subTest(paths=paths):
                with self.assertRaises(StudioWorkerError):
                    self.manifest("http://127.0.0.1:1234/v1", allowed_paths=paths).validate()

    def test_dirty_source_repository_fails_closed(self):
        (self.repo / "untracked.txt").write_text("dirty\n", encoding="utf-8")
        manifest = self.manifest("http://127.0.0.1:1234/v1")
        with self.assertRaisesRegex(StudioWorkerError, "clean"):
            run_manifest(manifest)
        self.assertNotIn("studio/test-change", git(self.repo, "branch", "--list"))

    def test_model_path_outside_allowlist_is_blocked_without_test_execution(self):
        outside = json.dumps(
            {
                "files": [{"path": "check.py", "content": "raise SystemExit(0)\n"}],
                "summary": "cheat",
            }
        )
        with FakeModelServer([outside]) as model:
            result = run_manifest(self.manifest(model.base_url))
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.stop_reason, "malformed_model_output")
        self.assertEqual(result.rounds[0].candidate_sha, None)
        self.assertEqual(
            Path(result.worktree_path, "check.py").read_text(encoding="utf-8"),
            (self.repo / "check.py").read_text(encoding="utf-8"),
        )

    def test_strict_json_rejects_markdown_wrapped_model_output(self):
        wrapped = "```json\n" + self.response(2) + "\n```"
        with FakeModelServer([wrapped]) as model:
            result = run_manifest(self.manifest(model.base_url))
        self.assertEqual(result.stop_reason, "malformed_model_output")
        self.assertIsNone(result.final_candidate_sha)

    def test_two_identical_no_change_responses_stop_as_stagnation(self):
        no_change = self.response(1)
        with FakeModelServer([no_change, no_change]) as model:
            result = run_manifest(self.manifest(model.base_url, max_rounds=3))
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.stop_reason, "stagnation")
        self.assertEqual([item.status for item in result.rounds], ["no_change", "no_change"])
        self.assertEqual(len(model.requests), 2)
        self.assertIsNone(result.final_candidate_sha)

    def test_baseline_pass_then_candidate_failure_stops_as_regression(self):
        (self.repo / "check.py").write_text(
            "from pathlib import Path\n"
            "text = Path('app.py').read_text(encoding='utf-8')\n"
            "raise SystemExit(0 if 'VALUE = 1' in text else 1)\n",
            encoding="utf-8",
        )
        git(self.repo, "add", "check.py")
        git(
            self.repo,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-q",
            "-m",
            "passing baseline",
        )
        self.base_sha = git(self.repo, "rev-parse", "HEAD")

        with FakeModelServer([self.response(2)]) as model:
            result = run_manifest(self.manifest(model.base_url, branch="studio/regression"))
        self.assertTrue(result.baseline_test.passed)
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.stop_reason, "regression")
        self.assertFalse(result.rounds[0].test.passed)

    def test_failed_repairs_stop_at_round_budget(self):
        with FakeModelServer([self.response(3), self.response(4)]) as model:
            result = run_manifest(
                self.manifest(model.base_url, branch="studio/round-budget", max_rounds=2)
            )
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.stop_reason, "round_budget_exhausted")
        self.assertEqual(len(result.rounds), 2)
        self.assertEqual(len(model.requests), 2)
        self.assertFalse(result.rounds[0].test.passed)
        self.assertFalse(result.rounds[1].test.passed)
        self.assertEqual(result.final_candidate_sha, result.rounds[-1].candidate_sha)

    def test_symlink_allowlist_target_is_rejected(self):
        link = self.repo / "linked.py"
        try:
            link.symlink_to(self.repo / "app.py")
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable")
        git(self.repo, "add", "linked.py")
        git(
            self.repo,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-q",
            "-m",
            "symlink",
        )
        self.base_sha = git(self.repo, "rev-parse", "HEAD")
        with FakeModelServer([self.response(2, path="linked.py")]) as model:
            with self.assertRaisesRegex(StudioWorkerError, "symlink"):
                run_manifest(
                    self.manifest(
                        model.base_url,
                        branch="studio/symlink",
                        allowed_paths=("linked.py",),
                    )
                )


if __name__ == "__main__":
    unittest.main()
