#!/usr/bin/env python3
"""Bounded local implementation worker for MIRA Studio.

This is an executable edge worker, not an authority boundary. The controller owns
Git identity, editable paths, test argv, model endpoint/model, budgets and stop
rules. Model output is treated only as untrusted file-replacement data.

The worker never merges, pushes, installs, publishes, activates, edits credentials,
or executes model-supplied commands. It creates an isolated Git worktree/branch
from an exact base SHA, talks only to a loopback OpenAI-compatible endpoint, runs
fixed tests with shell=False, and writes durable JSON evidence under the source
repository's .git directory.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time
from typing import Any
from urllib.parse import urlparse
import uuid


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DRAFT_RE = re.compile(r"^intake-[0-9a-f]{64}$")
_SAFE_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")
_MAX_ALLOWED_PATHS = 64
_MAX_SPEC_CHARS = 32_000
_MAX_FILE_BYTES = 512_000
_MAX_TOTAL_SOURCE_BYTES = 2_000_000
_MAX_MODEL_BODY_BYTES = 4_000_000
_MAX_STDIO_CHARS = 200_000


class StudioWorkerError(RuntimeError):
    """Fail-closed worker validation or execution error."""


@dataclasses.dataclass(frozen=True)
class WorkerManifest:
    draft_id: str
    objective: str
    repo_path: str
    base_sha: str
    branch_name: str
    allowed_paths: tuple[str, ...]
    test_argv: tuple[str, ...]
    model_base_url: str
    model: str
    max_rounds: int = 3
    wall_timeout_seconds: int = 900
    test_timeout_seconds: int = 180
    model_timeout_seconds: int = 180

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "WorkerManifest":
        expected = {
            "draft_id",
            "objective",
            "repo_path",
            "base_sha",
            "branch_name",
            "allowed_paths",
            "test_argv",
            "model_base_url",
            "model",
            "max_rounds",
            "wall_timeout_seconds",
            "test_timeout_seconds",
            "model_timeout_seconds",
        }
        unknown = set(raw) - expected
        if unknown:
            raise StudioWorkerError(
                "manifest contains unknown fields: " + ", ".join(sorted(unknown))
            )
        try:
            manifest = cls(
                draft_id=raw["draft_id"],
                objective=raw["objective"],
                repo_path=raw["repo_path"],
                base_sha=raw["base_sha"],
                branch_name=raw["branch_name"],
                allowed_paths=tuple(raw["allowed_paths"]),
                test_argv=tuple(raw["test_argv"]),
                model_base_url=raw["model_base_url"],
                model=raw["model"],
                max_rounds=int(raw.get("max_rounds", 3)),
                wall_timeout_seconds=int(raw.get("wall_timeout_seconds", 900)),
                test_timeout_seconds=int(raw.get("test_timeout_seconds", 180)),
                model_timeout_seconds=int(raw.get("model_timeout_seconds", 180)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise StudioWorkerError(f"invalid manifest: {exc}") from exc
        manifest.validate()
        return manifest

    def validate(self) -> None:
        if not isinstance(self.draft_id, str) or not _DRAFT_RE.fullmatch(self.draft_id):
            raise StudioWorkerError("draft_id must be an intake SHA-256 identity")
        _nonblank(self.objective, "objective", _MAX_SPEC_CHARS)
        _nonblank(self.repo_path, "repo_path", 4096)
        if not isinstance(self.base_sha, str) or not _SHA_RE.fullmatch(self.base_sha):
            raise StudioWorkerError("base_sha must be a lowercase 40-character Git SHA")
        if (
            not isinstance(self.branch_name, str)
            or not _SAFE_BRANCH_RE.fullmatch(self.branch_name)
            or ".." in self.branch_name
            or "//" in self.branch_name
            or self.branch_name.endswith(("/", ".", ".lock"))
        ):
            raise StudioWorkerError("branch_name is not a safe Git branch name")
        if not self.allowed_paths or len(self.allowed_paths) > _MAX_ALLOWED_PATHS:
            raise StudioWorkerError(
                f"allowed_paths must contain 1..{_MAX_ALLOWED_PATHS} paths"
            )
        canonical_paths = tuple(sorted(set(_safe_relpath(p) for p in self.allowed_paths)))
        if self.allowed_paths != canonical_paths:
            raise StudioWorkerError(
                "allowed_paths must be canonical, unique, and sorted"
            )
        if not self.test_argv or len(self.test_argv) > 64:
            raise StudioWorkerError("test_argv must contain 1..64 fixed arguments")
        for index, value in enumerate(self.test_argv):
            _nonblank(value, f"test_argv[{index}]", 4096)
        _validate_loopback_base_url(self.model_base_url)
        _nonblank(self.model, "model", 512)
        _bounded_int(self.max_rounds, "max_rounds", 1, 12)
        _bounded_int(self.wall_timeout_seconds, "wall_timeout_seconds", 5, 7200)
        _bounded_int(self.test_timeout_seconds, "test_timeout_seconds", 1, 1800)
        _bounded_int(self.model_timeout_seconds, "model_timeout_seconds", 1, 1800)


@dataclasses.dataclass(frozen=True)
class TestEvidence:
    candidate_sha: str
    returncode: int | None
    timed_out: bool
    duration_ms: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return not self.timed_out and self.returncode == 0


@dataclasses.dataclass(frozen=True)
class RoundEvidence:
    round_index: int
    model_response_sha256: str
    changed_paths: tuple[str, ...]
    candidate_sha: str | None
    test: TestEvidence | None
    status: str


@dataclasses.dataclass(frozen=True)
class WorkerResult:
    run_id: str
    draft_id: str
    source_repo: str
    base_sha: str
    branch_name: str
    worktree_path: str
    evidence_path: str
    status: str
    stop_reason: str
    baseline_test: TestEvidence
    rounds: tuple[RoundEvidence, ...]
    final_candidate_sha: str | None

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class _NoRedirectConnection:
    """Small explicit HTTP client so redirects cannot escape loopback policy."""

    def __init__(self, base_url: str, timeout: int) -> None:
        parsed = _validate_loopback_base_url(base_url)
        self._parsed = parsed
        self._timeout = timeout

    def chat(self, *, model: str, messages: list[dict[str, str]]) -> str:
        body = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": 0,
                "stream": False,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(body) > _MAX_MODEL_BODY_BYTES:
            raise StudioWorkerError("model request exceeds bounded body size")
        path_prefix = self._parsed.path.rstrip("/")
        target = f"{path_prefix}/chat/completions" or "/chat/completions"
        connection_cls = (
            http.client.HTTPSConnection
            if self._parsed.scheme == "https"
            else http.client.HTTPConnection
        )
        conn = connection_cls(
            self._parsed.hostname,
            self._parsed.port,
            timeout=self._timeout,
        )
        try:
            conn.request(
                "POST",
                target,
                body=body,
                headers={"Content-Type": "application/json"},
            )
            response = conn.getresponse()
            raw = response.read(_MAX_MODEL_BODY_BYTES + 1)
            if len(raw) > _MAX_MODEL_BODY_BYTES:
                raise StudioWorkerError("model response exceeds bounded body size")
            if response.status != 200:
                raise StudioWorkerError(
                    f"model endpoint returned HTTP {response.status}"
                )
            try:
                payload = json.loads(raw.decode("utf-8"))
                content = payload["choices"][0]["message"]["content"]
            except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                raise StudioWorkerError("model endpoint returned malformed response") from exc
            if not isinstance(content, str):
                raise StudioWorkerError("model message content must be text")
            return content
        finally:
            conn.close()


def run_manifest(manifest: WorkerManifest) -> WorkerResult:
    """Execute one bounded Studio implementation attempt."""

    manifest.validate()
    started = time.monotonic()
    repo = _validate_repo(manifest)
    git_dir = Path(_git(repo, "rev-parse", "--git-dir").stdout.strip())
    if not git_dir.is_absolute():
        git_dir = (repo / git_dir).resolve()
    run_id = f"studio-{int(time.time())}-{uuid.uuid4().hex[:12]}"
    evidence_dir = git_dir / "mira-studio-runs" / run_id
    evidence_dir.mkdir(parents=True, exist_ok=False)
    worktree_root = repo.parent / ".mira-studio-worktrees"
    worktree_root.mkdir(parents=True, exist_ok=True)
    worktree = worktree_root / run_id

    _git(repo, "worktree", "add", "-b", manifest.branch_name, str(worktree), manifest.base_sha)
    try:
        _validate_allowed_paths_in_worktree(worktree, manifest.allowed_paths)
        baseline = _run_tests(worktree, manifest.test_argv, manifest.test_timeout_seconds)
        _write_json(evidence_dir / "baseline.json", dataclasses.asdict(baseline))

        rounds: list[RoundEvidence] = []
        previous_response_sha: str | None = None
        repeated_response_count = 0
        prior_test = baseline
        final_sha: str | None = None
        model_client = _NoRedirectConnection(
            manifest.model_base_url, manifest.model_timeout_seconds
        )

        status = "blocked"
        stop_reason = "round_budget_exhausted"

        for round_index in range(1, manifest.max_rounds + 1):
            if time.monotonic() - started >= manifest.wall_timeout_seconds:
                stop_reason = "wall_timeout"
                break

            source_snapshot = _source_snapshot(worktree, manifest.allowed_paths)
            prompt = _build_prompt(
                manifest,
                round_index=round_index,
                source_snapshot=source_snapshot,
                prior_test=prior_test,
            )
            response_text = model_client.chat(
                model=manifest.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a bounded MIRA Studio implementation worker. "
                            "Return only the required JSON object. Never return commands, "
                            "paths outside the supplied allowlist, markdown, or prose."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            response_sha = _sha256_bytes(response_text.encode("utf-8"))
            if response_sha == previous_response_sha:
                repeated_response_count += 1
            else:
                repeated_response_count = 1
            previous_response_sha = response_sha

            try:
                replacements = _parse_model_replacements(
                    response_text, manifest.allowed_paths
                )
                changed_paths = _apply_replacements(worktree, replacements)
            except StudioWorkerError:
                record = RoundEvidence(
                    round_index=round_index,
                    model_response_sha256=response_sha,
                    changed_paths=(),
                    candidate_sha=None,
                    test=None,
                    status="malformed_model_output",
                )
                rounds.append(record)
                _write_json(
                    evidence_dir / f"round-{round_index:02d}.json",
                    dataclasses.asdict(record),
                )
                stop_reason = "malformed_model_output"
                break

            if not changed_paths:
                record = RoundEvidence(
                    round_index=round_index,
                    model_response_sha256=response_sha,
                    changed_paths=(),
                    candidate_sha=None,
                    test=None,
                    status="no_change",
                )
                rounds.append(record)
                _write_json(
                    evidence_dir / f"round-{round_index:02d}.json",
                    dataclasses.asdict(record),
                )
                if repeated_response_count >= 2:
                    stop_reason = "stagnation"
                    break
                continue

            _assert_only_allowed_changes(worktree, manifest.allowed_paths)
            candidate_sha = _commit_candidate(worktree, round_index, changed_paths)
            final_sha = candidate_sha
            test = _run_tests(
                worktree, manifest.test_argv, manifest.test_timeout_seconds
            )
            prior_test = test
            round_status = "passed" if test.passed else "failed"
            record = RoundEvidence(
                round_index=round_index,
                model_response_sha256=response_sha,
                changed_paths=changed_paths,
                candidate_sha=candidate_sha,
                test=test,
                status=round_status,
            )
            rounds.append(record)
            _write_json(
                evidence_dir / f"round-{round_index:02d}.json",
                dataclasses.asdict(record),
            )

            if test.passed:
                status = "ready_for_review"
                stop_reason = "tests_passed"
                break
            if baseline.passed:
                status = "blocked"
                stop_reason = "regression"
                break
            if time.monotonic() - started >= manifest.wall_timeout_seconds:
                stop_reason = "wall_timeout"
                break

        result = WorkerResult(
            run_id=run_id,
            draft_id=manifest.draft_id,
            source_repo=str(repo),
            base_sha=manifest.base_sha,
            branch_name=manifest.branch_name,
            worktree_path=str(worktree),
            evidence_path=str(evidence_dir),
            status=status,
            stop_reason=stop_reason,
            baseline_test=baseline,
            rounds=tuple(rounds),
            final_candidate_sha=final_sha,
        )
        _write_json(evidence_dir / "result.json", result.as_dict())
        return result
    except Exception as exc:
        _write_json(
            evidence_dir / "worker-error.json",
            {"type": type(exc).__name__, "message": str(exc)},
        )
        raise


def _validate_repo(manifest: WorkerManifest) -> Path:
    repo = Path(manifest.repo_path).expanduser().resolve(strict=True)
    if not repo.is_dir():
        raise StudioWorkerError("repo_path must be a directory")
    root = Path(_git(repo, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if root != repo:
        raise StudioWorkerError("repo_path must be the Git worktree root")
    if _git(repo, "status", "--porcelain").stdout.strip():
        raise StudioWorkerError("source repository must be clean")
    resolved_base = _git(repo, "rev-parse", f"{manifest.base_sha}^{{commit}}").stdout.strip()
    if resolved_base != manifest.base_sha:
        raise StudioWorkerError("base_sha does not resolve exactly to the requested commit")
    existing = _git(repo, "show-ref", "--verify", f"refs/heads/{manifest.branch_name}", check=False)
    if existing.returncode == 0:
        raise StudioWorkerError("branch_name already exists")
    branch_check = _git(repo, "check-ref-format", "--branch", manifest.branch_name, check=False)
    if branch_check.returncode != 0:
        raise StudioWorkerError("branch_name fails Git ref validation")
    return repo


def _safe_parent(worktree: Path, rel: str) -> Path:
    """Return/create a parent path without ever traversing a symlink.

    Parent components are checked one at a time before creation. This is deliberate:
    calling mkdir(parents=True) first could follow a repository symlink and create
    directories outside the isolated worktree before the escape was noticed.
    """

    root = worktree.resolve()
    current = root
    for part in PurePosixPath(rel).parts[:-1]:
        candidate = current / part
        if candidate.is_symlink():
            raise StudioWorkerError(f"allowed path traverses symlink: {rel}")
        if candidate.exists():
            if not candidate.is_dir():
                raise StudioWorkerError(
                    f"allowed path parent is not a directory: {rel}"
                )
        else:
            candidate.mkdir()
        if candidate.is_symlink():
            raise StudioWorkerError(f"allowed path traverses symlink: {rel}")
        resolved = candidate.resolve()
        if root != resolved and root not in resolved.parents:
            raise StudioWorkerError(f"allowed path escapes worktree: {rel}")
        current = candidate
    return current


def _validate_allowed_paths_in_worktree(worktree: Path, paths: tuple[str, ...]) -> None:
    for rel in paths:
        target = worktree / rel
        _safe_parent(worktree, rel)
        if target.is_symlink():
            raise StudioWorkerError(f"allowed path is a symlink: {rel}")
        if target.exists() and not target.is_file():
            raise StudioWorkerError(f"allowed path is not a regular file: {rel}")


def _source_snapshot(worktree: Path, paths: tuple[str, ...]) -> dict[str, str]:
    total = 0
    snapshot: dict[str, str] = {}
    for rel in paths:
        target = worktree / rel
        if not target.exists():
            snapshot[rel] = ""
            continue
        raw = target.read_bytes()
        if len(raw) > _MAX_FILE_BYTES:
            raise StudioWorkerError(f"source file exceeds size limit: {rel}")
        total += len(raw)
        if total > _MAX_TOTAL_SOURCE_BYTES:
            raise StudioWorkerError("source snapshot exceeds total size limit")
        try:
            snapshot[rel] = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise StudioWorkerError(f"source file is not UTF-8 text: {rel}") from exc
    return snapshot


def _build_prompt(
    manifest: WorkerManifest,
    *,
    round_index: int,
    source_snapshot: dict[str, str],
    prior_test: TestEvidence,
) -> str:
    contract = {
        "draft_id": manifest.draft_id,
        "objective": manifest.objective,
        "round": round_index,
        "allowed_paths": list(manifest.allowed_paths),
        "fixed_test_argv": list(manifest.test_argv),
        "current_files": source_snapshot,
        "previous_test": dataclasses.asdict(prior_test),
        "response_schema": {
            "files": [
                {"path": "one exact allowed path", "content": "complete UTF-8 file contents"}
            ],
            "summary": "short implementation summary",
        },
        "rules": [
            "Return exactly one JSON object and no markdown/prose outside it.",
            "Only replace files named in allowed_paths.",
            "Return complete file contents, not patches.",
            "Do not return shell commands or request additional tools.",
            "Do not modify tests unless a test path is explicitly allowlisted.",
            "Preserve unrelated behavior and repair the previous test failure when present.",
        ],
    }
    return json.dumps(contract, ensure_ascii=False, sort_keys=True)


def _parse_model_replacements(
    response_text: str,
    allowed_paths: tuple[str, ...],
) -> dict[str, str]:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise StudioWorkerError("model output must be strict JSON") from exc
    if not isinstance(payload, dict) or set(payload) != {"files", "summary"}:
        raise StudioWorkerError("model output must contain exactly files and summary")
    if not isinstance(payload["summary"], str) or len(payload["summary"]) > 2000:
        raise StudioWorkerError("model summary must be bounded text")
    files = payload["files"]
    if not isinstance(files, list) or not files or len(files) > len(allowed_paths):
        raise StudioWorkerError("model files must be a non-empty bounded list")
    allowed = set(allowed_paths)
    replacements: dict[str, str] = {}
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "content"}:
            raise StudioWorkerError("each model file entry must contain path and content")
        path = item["path"]
        content = item["content"]
        if not isinstance(path, str) or _safe_relpath(path) != path or path not in allowed:
            raise StudioWorkerError("model attempted a path outside the allowlist")
        if path in replacements:
            raise StudioWorkerError("model returned a duplicate path")
        if not isinstance(content, str):
            raise StudioWorkerError("model file content must be text")
        encoded = content.encode("utf-8")
        if len(encoded) > _MAX_FILE_BYTES:
            raise StudioWorkerError("model file content exceeds size limit")
        replacements[path] = content
    return replacements


def _apply_replacements(worktree: Path, replacements: dict[str, str]) -> tuple[str, ...]:
    changed: list[str] = []
    for rel, content in replacements.items():
        target = worktree / rel
        _safe_parent(worktree, rel)
        if target.is_symlink():
            raise StudioWorkerError(f"refusing to replace symlink: {rel}")
        if target.exists() and not target.is_file():
            raise StudioWorkerError(f"refusing to replace non-file: {rel}")
        previous = target.read_bytes() if target.exists() else None
        updated = content.encode("utf-8")
        if previous == updated:
            continue
        temp = target.with_name(f".{target.name}.mira-{uuid.uuid4().hex}.tmp")
        try:
            with temp.open("wb") as handle:
                handle.write(updated)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        finally:
            if temp.exists():
                temp.unlink()
        changed.append(rel)
    return tuple(sorted(changed))


def _assert_only_allowed_changes(worktree: Path, allowed_paths: tuple[str, ...]) -> None:
    status = _git(worktree, "status", "--porcelain=v1", "-z").stdout
    records = [record for record in status.split("\0") if record]
    changed: set[str] = set()
    for record in records:
        if len(record) < 4:
            raise StudioWorkerError("unable to parse Git status")
        path = record[3:]
        if " -> " in path:
            raise StudioWorkerError("renames are not permitted")
        changed.add(path)
    outside = changed - set(allowed_paths)
    if outside:
        raise StudioWorkerError(
            "worktree changed outside allowlist: " + ", ".join(sorted(outside))
        )


def _commit_candidate(
    worktree: Path, round_index: int, changed_paths: tuple[str, ...]
) -> str:
    _git(worktree, "add", "--", *changed_paths)
    staged = tuple(
        sorted(
            line
            for line in _git(worktree, "diff", "--cached", "--name-only").stdout.splitlines()
            if line
        )
    )
    if staged != changed_paths:
        raise StudioWorkerError("staged paths do not match the validated change set")
    _git(
        worktree,
        "-c",
        "user.name=MIRA Studio Worker",
        "-c",
        "user.email=mira-studio-worker@invalid",
        "commit",
        "--no-gpg-sign",
        "-m",
        f"MIRA Studio candidate round {round_index}",
    )
    sha = _git(worktree, "rev-parse", "HEAD").stdout.strip()
    if not _SHA_RE.fullmatch(sha):
        raise StudioWorkerError("candidate commit did not produce a valid Git SHA")
    return sha


def _run_tests(worktree: Path, argv: tuple[str, ...], timeout_seconds: int) -> TestEvidence:
    candidate_sha = _git(worktree, "rev-parse", "HEAD").stdout.strip()
    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(argv),
            cwd=worktree,
            shell=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration_ms = int((time.monotonic() - started) * 1000)
        return TestEvidence(
            candidate_sha=candidate_sha,
            returncode=completed.returncode,
            timed_out=False,
            duration_ms=duration_ms,
            stdout=_bounded_stdio(completed.stdout),
            stderr=_bounded_stdio(completed.stderr),
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        return TestEvidence(
            candidate_sha=candidate_sha,
            returncode=None,
            timed_out=True,
            duration_ms=duration_ms,
            stdout=_bounded_stdio(_coerce_timeout_stream(exc.stdout)),
            stderr=_bounded_stdio(_coerce_timeout_stream(exc.stderr)),
        )


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        shell=False,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        raise StudioWorkerError(
            f"git {' '.join(args[:2])} failed: {_bounded_stdio(completed.stderr).strip()}"
        )
    return completed


def _safe_relpath(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise StudioWorkerError("editable paths must be non-empty POSIX relative paths")
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix():
        raise StudioWorkerError("editable paths must be canonical POSIX relative paths")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise StudioWorkerError("editable paths may not contain traversal components")
    if path.parts[0] == ".git":
        raise StudioWorkerError("editable paths may not target .git")
    return value


def _validate_loopback_base_url(value: str):
    _nonblank(value, "model_base_url", 2048)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise StudioWorkerError("model_base_url must use http or https")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise StudioWorkerError("model_base_url may not contain credentials/query/fragment")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise StudioWorkerError("model_base_url must resolve explicitly to loopback")
    if parsed.path not in {"", "/", "/v1", "/v1/"}:
        raise StudioWorkerError("model_base_url path must be empty or /v1")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise StudioWorkerError("model_base_url contains invalid port") from exc
    return parsed


def _nonblank(value: object, field: str, max_chars: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StudioWorkerError(f"{field} must be non-blank text")
    if value != value.strip():
        raise StudioWorkerError(f"{field} must not have surrounding whitespace")
    if len(value) > max_chars:
        raise StudioWorkerError(f"{field} exceeds {max_chars} characters")
    return value


def _bounded_int(value: object, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StudioWorkerError(f"{field} must be an integer")
    if value < minimum or value > maximum:
        raise StudioWorkerError(f"{field} must be between {minimum} and {maximum}")
    return value


def _bounded_stdio(value: str) -> str:
    if len(value) <= _MAX_STDIO_CHARS:
        return value
    return value[:_MAX_STDIO_CHARS] + "\n...[truncated]"


def _coerce_timeout_stream(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    encoded = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    try:
        with temp.open("wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def _load_manifest(path: Path) -> WorkerManifest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StudioWorkerError(f"unable to read manifest: {exc}") from exc
    if not isinstance(raw, dict):
        raise StudioWorkerError("manifest root must be a JSON object")
    return WorkerManifest.from_json(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to a bounded Studio worker manifest")
    args = parser.parse_args(argv)
    try:
        result = run_manifest(_load_manifest(args.manifest.resolve(strict=True)))
    except StudioWorkerError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result.as_dict(), sort_keys=True))
    return 0 if result.status == "ready_for_review" else 1


if __name__ == "__main__":
    sys.exit(main())