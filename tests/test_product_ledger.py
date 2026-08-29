from __future__ import annotations

import unittest

from mira.product_ledger import (
    ProductLedgerError,
    load_product_ledger,
    normalize_work_status,
    parse_backlog,
)


class ProductLedgerTests(unittest.TestCase):
    def test_normalizes_status_conservatively(self) -> None:
        self.assertEqual(normalize_work_status("complete; merged/test-verified"), "completed")
        self.assertEqual(normalize_work_status("queued after dependency"), "queued")
        self.assertEqual(normalize_work_status("deferred optional"), "deferred")
        self.assertEqual(normalize_work_status("paused at provider checkpoint"), "paused")
        self.assertEqual(normalize_work_status("split; children below"), "split")
        self.assertEqual(normalize_work_status("policy active; automation queued"), "active")
        self.assertEqual(normalize_work_status("some bespoke prose"), "unknown")

    def test_parses_ranked_and_unranked_work_tables(self) -> None:
        backlog = """# BACKLOG

| Rank | Work ID | Class | Work | Dependencies | Status |
|---:|---|---|---|---|---|
| 1 | `A-WORK-001` | BLOCKER | First thing | F-001 | complete |
| 2 | `B-WORK-001` | PREREQUISITE | Second thing | A-WORK-001 | queued |

## Later

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `C-WORK-001` | LATER | Third thing | - | deferred |
"""
        records = parse_backlog(backlog)
        self.assertEqual([record.work_id for record in records], ["A-WORK-001", "B-WORK-001", "C-WORK-001"])
        self.assertEqual(records[0].lifecycle_state, "completed")
        self.assertEqual(records[1].lifecycle_state, "queued")
        self.assertEqual(records[2].lifecycle_state, "deferred")

    def test_duplicate_work_id_fails(self) -> None:
        backlog = """| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `A-WORK-001` | BLOCKER | First | - | queued |
| `A-WORK-001` | LATER | Duplicate | - | deferred |
"""
        with self.assertRaisesRegex(ProductLedgerError, "duplicate backlog work ID"):
            parse_backlog(backlog)

    def test_real_repository_ledger_is_valid_and_keeps_completed_work(self) -> None:
        ledger = load_product_ledger()
        feature_ids = {feature.feature_id for feature in ledger.feature_registry.features}
        work = {record.work_id: record for record in ledger.work}
        self.assertIn("RECEIPT-001", feature_ids)
        self.assertIn("MEAL-001", feature_ids)
        self.assertIn("WEARABLE-001", feature_ids)
        self.assertIn("CORE-ROUNDTRIP", work)
        self.assertEqual(work["CORE-ROUNDTRIP"].lifecycle_state, "completed")
        self.assertNotIn("CORE-ROUNDTRIP", {item.work_id for item in ledger.selectable_work()})

    def test_selectable_work_keeps_active_unknown_and_queued_but_not_inactive(self) -> None:
        backlog = """| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `DONE-001` | BLOCKER | Done | - | complete |
| `NOW-001` | BLOCKER | Now | - | active |
| `NEXT-001` | PREREQUISITE | Next | - | queued |
| `ODD-001` | VERTICAL | Odd | - | bespoke status |
| `LATER-001` | LATER | Later | - | deferred |
"""
        records = parse_backlog(backlog)
        active = [record.work_id for record in records if record.lifecycle_state not in {"completed", "deferred", "paused", "split", "rejected"}]
        self.assertEqual(active, ["NOW-001", "NEXT-001", "ODD-001"])


if __name__ == "__main__":
    unittest.main()
