from __future__ import annotations

import unittest

from mira.work_session_alignment import (
    WorkSessionAlignmentError,
    check_alignment_texts,
    check_paths,
)


FEATURES = """# MIRA 2.0 FEATURES

## Feature index

`ID | Title | requirement | evidence | deps`

- `CORE-001` | MIRA identity | required | specified | -
- `ONBOARD-002` | Sanitized starter | required | specified | -
- `ONBOARD-003` | Four-question setup | required | specified | ONBOARD-002
- `SERVICE-001` | Service state | required | specified | -
- `CAL-006` | Calendar preference | required | specified | -
- `STUDIO-001` | MIRA Studio | required | specified | -
- `API-001` | API | required | specified | -
- `AUTH-001` | Authority | required | specified | -
- `STORE-001` | Store | required | specified | -
- `RECOVERY-002` | Isolation | required | specified | -
- `ONBOARD-006` | Browser install | required | specified | -

## Mappings
"""

BACKLOG = """# BACKLOG

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `FIRSTBOOT-CORE-001` | PREREQUISITE | First boot | ONBOARD-003 | queued |
"""

ROADMAP = """# ROADMAP

The ordinary Personal Google path must be useful without servers.
"""

CURRENT = """# CURRENT WORK

## Active packet

### `M2-M0-007` — No-app first boot

- **Primary work:** `FIRSTBOOT-CORE-001`
- **Primary features:** `ONBOARD-003`, `ONBOARD-002`, `CORE-001`
- **Related invariants/features:** `SERVICE-001`, `CAL-006`, `STUDIO-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`
checked

### `BACKLOG.md`
checked

### `ROADMAP.md`
checked

### Direction result

ALIGNED
"""


class WorkSessionAlignmentTests(unittest.TestCase):
    def test_valid_alignment(self) -> None:
        report = check_alignment_texts(
            current_work=CURRENT,
            features=FEATURES,
            backlog=BACKLOG,
            roadmap=ROADMAP,
        )
        self.assertEqual(report.packet_id, "M2-M0-007")
        self.assertEqual(report.primary_work_ids, ("FIRSTBOOT-CORE-001",))
        self.assertIn("ONBOARD-003", report.feature_ids)

    def test_unknown_work_fails(self) -> None:
        broken = CURRENT.replace("FIRSTBOOT-CORE-001", "MISSING-WORK-001")
        with self.assertRaisesRegex(WorkSessionAlignmentError, "BACKLOG"):
            check_alignment_texts(
                current_work=broken,
                features=FEATURES,
                backlog=BACKLOG,
                roadmap=ROADMAP,
            )

    def test_unknown_feature_fails(self) -> None:
        broken = CURRENT.replace("ONBOARD-003", "BOGUS-999")
        with self.assertRaisesRegex(WorkSessionAlignmentError, "FEATURES"):
            check_alignment_texts(
                current_work=broken,
                features=FEATURES,
                backlog=BACKLOG,
                roadmap=ROADMAP,
            )

    def test_missing_authority_review_fails(self) -> None:
        broken = CURRENT.replace("### `ROADMAP.md`", "### roadmap")
        with self.assertRaisesRegex(WorkSessionAlignmentError, "ROADMAP"):
            check_alignment_texts(
                current_work=broken,
                features=FEATURES,
                backlog=BACKLOG,
                roadmap=ROADMAP,
            )

    def test_direction_must_be_aligned(self) -> None:
        broken = CURRENT.replace("ALIGNED", "NOT CHECKED")
        with self.assertRaisesRegex(WorkSessionAlignmentError, "ALIGNED"):
            check_alignment_texts(
                current_work=broken,
                features=FEATURES,
                backlog=BACKLOG,
                roadmap=ROADMAP,
            )

    def test_repository_current_work_is_aligned(self) -> None:
        report = check_paths()
        self.assertEqual(report.packet_id, "M2-M0-007")
        self.assertIn("FIRSTBOOT-CORE-001", report.primary_work_ids)


if __name__ == "__main__":
    unittest.main()
