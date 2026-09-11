from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import unittest

from mira.feature_share import build_feature_share_package
from mira.feature_share_transport import (
    FeatureShareTransportError,
    ShareWriteResult,
    authorize_feature_share_publication,
    import_feature_share,
    publish_feature_share,
)


SOURCE_DIGEST = hashlib.sha256(b"reviewed-source").hexdigest()


def build_package():
    return build_feature_share_package(
        private_owner_id="private-owner-001",
        change_id="CHANGE-001",
        source_revision="abc1234",
        reviewed_source_sha256=SOURCE_DIGEST,
        feature_ids=("DEV-004", "STUDIO-001"),
        dependency_ids=("DIST-001", "SOURCE-001"),
        min_runtime_schema=1,
        max_runtime_schema=3,
        artifacts={"mira/example.py": "VALUE = 1\n"},
    )


def authorization(package_id: str):
    return authorize_feature_share_publication(
        private_actor_id="private-publisher-001",
        authorization_id="AUTH-001",
        package_id=package_id,
        destination="community/stable",
    )


class MemoryShareStore:
    def __init__(self):
        self.data: dict[tuple[str, str], bytes] = {}
        self.write_calls = 0
        self.read_calls = 0
        self.write_exception = False
        self.write_before_exception = False
        self.read_exception_at: int | None = None
        self.write_outcome = "performed"
        self.remote_revision = "rev-1"
        self.tamper_after_write: bytes | None = None
        self.malformed_write_result = False

    def read_package(self, *, destination: str, package_id: str):
        self.read_calls += 1
        if self.read_exception_at == self.read_calls:
            raise RuntimeError("read failed")
        return self.data.get((destination, package_id))

    def write_package(self, *, destination: str, package_id: str, payload: bytes):
        self.write_calls += 1
        stored = self.tamper_after_write if self.tamper_after_write is not None else payload
        if self.write_before_exception:
            self.data[(destination, package_id)] = stored
        if self.write_exception:
            raise RuntimeError("write failed after unknown provider outcome")
        self.data[(destination, package_id)] = stored
        if self.malformed_write_result:
            return {"outcome": "performed"}
        return ShareWriteResult(
            outcome=self.write_outcome,
            remote_revision=self.remote_revision,
        )


class FeatureShareTransportTests(unittest.TestCase):
    def test_authorization_hides_private_actor(self):
        package = build_package()
        auth = authorization(package.package_id)
        self.assertNotEqual(auth.actor_fingerprint, "private-publisher-001")
        self.assertEqual(len(auth.actor_fingerprint), 64)

    def test_publish_success_requires_exact_readback(self):
        package = build_package()
        store = MemoryShareStore()
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertTrue(receipt.verified)
        self.assertFalse(receipt.recovery_required)
        self.assertEqual(receipt.write_state, "performed")
        self.assertEqual(store.write_calls, 1)
        self.assertFalse(receipt.activation_authorized)
        self.assertFalse(receipt.source_mutation_authorized)
        self.assertFalse(receipt.install_authorized)

    def test_identical_remote_package_is_zero_write_replay(self):
        package = build_package()
        store = MemoryShareStore()
        store.data[("community/stable", package.package_id)] = package.canonical_bytes()
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertTrue(receipt.verified)
        self.assertTrue(receipt.replay)
        self.assertEqual(receipt.write_state, "not_attempted")
        self.assertEqual(store.write_calls, 0)

    def test_conflicting_existing_bytes_fail_before_write(self):
        package = build_package()
        store = MemoryShareStore()
        store.data[("community/stable", package.package_id)] = b"not-the-package\n"
        with self.assertRaisesRegex(FeatureShareTransportError, "different bytes"):
            publish_feature_share(
                package.projection(), authorization=authorization(package.package_id), store=store
            )
        self.assertEqual(store.write_calls, 0)

    def test_denied_authorization_fails_before_store_access(self):
        package = build_package()
        store = MemoryShareStore()
        denied = replace(authorization(package.package_id), authorized=False)
        with self.assertRaisesRegex(FeatureShareTransportError, "denied"):
            publish_feature_share(package.projection(), authorization=denied, store=store)
        self.assertEqual(store.read_calls, 0)
        self.assertEqual(store.write_calls, 0)

    def test_authorization_for_another_package_fails(self):
        package = build_package()
        store = MemoryShareStore()
        foreign = replace(authorization(package.package_id), package_id="0" * 64)
        with self.assertRaisesRegex(FeatureShareTransportError, "another package"):
            publish_feature_share(package.projection(), authorization=foreign, store=store)
        self.assertEqual(store.write_calls, 0)

    def test_invalid_destination_namespace_fails(self):
        package = build_package()
        store = MemoryShareStore()
        bad = replace(authorization(package.package_id), destination="https://example.com/private")
        with self.assertRaisesRegex(FeatureShareTransportError, "symbolic share namespace"):
            publish_feature_share(package.projection(), authorization=bad, store=store)
        self.assertEqual(store.write_calls, 0)

    def test_preflight_read_failure_is_not_clean_absence(self):
        package = build_package()
        store = MemoryShareStore()
        store.read_exception_at = 1
        with self.assertRaisesRegex(FeatureShareTransportError, "preflight remote read failed"):
            publish_feature_share(
                package.projection(), authorization=authorization(package.package_id), store=store
            )
        self.assertEqual(store.write_calls, 0)

    def test_write_exception_without_exact_remote_state_requires_recovery(self):
        package = build_package()
        store = MemoryShareStore()
        store.write_exception = True
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertFalse(receipt.verified)
        self.assertTrue(receipt.recovery_required)
        self.assertEqual(receipt.write_state, "unknown")

    def test_write_exception_after_actual_write_is_reconciled_by_exact_readback(self):
        package = build_package()
        store = MemoryShareStore()
        store.write_before_exception = True
        store.write_exception = True
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertTrue(receipt.verified)
        self.assertFalse(receipt.recovery_required)
        self.assertEqual(receipt.write_state, "unknown")

    def test_unknown_write_outcome_is_reconciled_by_exact_readback(self):
        package = build_package()
        store = MemoryShareStore()
        store.write_outcome = "unknown"
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertTrue(receipt.verified)
        self.assertFalse(receipt.recovery_required)
        self.assertEqual(receipt.write_state, "unknown")

    def test_unknown_write_outcome_with_mismatch_requires_recovery(self):
        package = build_package()
        store = MemoryShareStore()
        store.write_outcome = "unknown"
        store.tamper_after_write = b"tampered\n"
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertFalse(receipt.verified)
        self.assertTrue(receipt.recovery_required)
        self.assertEqual(receipt.write_state, "unknown")

    def test_post_write_read_failure_becomes_recovery_required(self):
        package = build_package()
        store = MemoryShareStore()
        store.read_exception_at = 2
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertTrue(receipt.recovery_required)
        self.assertFalse(receipt.verified)
        self.assertEqual(receipt.write_state, "performed")

    def test_post_write_tamper_becomes_recovery_required(self):
        package = build_package()
        store = MemoryShareStore()
        store.tamper_after_write = b"tampered\n"
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertTrue(receipt.recovery_required)
        self.assertFalse(receipt.verified)

    def test_malformed_write_result_fails_closed(self):
        package = build_package()
        store = MemoryShareStore()
        store.malformed_write_result = True
        with self.assertRaisesRegex(FeatureShareTransportError, "malformed write result"):
            publish_feature_share(
                package.projection(), authorization=authorization(package.package_id), store=store
            )

    def test_import_success_is_inert_and_reports_dependency_state(self):
        package = build_package()
        store = MemoryShareStore()
        store.data[("community/stable", package.package_id)] = package.canonical_bytes()
        imported = import_feature_share(
            destination="community/stable",
            package_id=package.package_id,
            store=store,
            runtime_schema=2,
            available_feature_ids=("DIST-001", "SOURCE-001"),
        )
        self.assertTrue(imported.inspection.ready_for_review)
        self.assertFalse(imported.activation_authorized)
        self.assertFalse(imported.source_mutation_authorized)
        self.assertFalse(imported.install_authorized)

    def test_import_reports_missing_dependency_without_authority(self):
        package = build_package()
        store = MemoryShareStore()
        store.data[("community/stable", package.package_id)] = package.canonical_bytes()
        imported = import_feature_share(
            destination="community/stable",
            package_id=package.package_id,
            store=store,
            runtime_schema=2,
            available_feature_ids=("DIST-001",),
        )
        self.assertEqual(imported.inspection.missing_dependencies, ("SOURCE-001",))
        self.assertFalse(imported.inspection.ready_for_review)
        self.assertFalse(imported.activation_authorized)

    def test_import_reports_runtime_incompatibility(self):
        package = build_package()
        store = MemoryShareStore()
        store.data[("community/stable", package.package_id)] = package.canonical_bytes()
        imported = import_feature_share(
            destination="community/stable",
            package_id=package.package_id,
            store=store,
            runtime_schema=4,
            available_feature_ids=("DIST-001", "SOURCE-001"),
        )
        self.assertFalse(imported.inspection.compatible)
        self.assertFalse(imported.inspection.ready_for_review)

    def test_import_wrong_requested_identity_fails(self):
        package = build_package()
        store = MemoryShareStore()
        requested = "0" * 64
        store.data[("community/stable", requested)] = package.canonical_bytes()
        with self.assertRaisesRegex(FeatureShareTransportError, "identity does not match"):
            import_feature_share(
                destination="community/stable",
                package_id=requested,
                store=store,
                runtime_schema=2,
                available_feature_ids=("DIST-001", "SOURCE-001"),
            )

    def test_import_noncanonical_json_fails(self):
        package = build_package()
        store = MemoryShareStore()
        noncanonical = json.dumps(package.projection(), indent=2, sort_keys=False).encode("utf-8")
        store.data[("community/stable", package.package_id)] = noncanonical
        with self.assertRaisesRegex(FeatureShareTransportError, "not canonical"):
            import_feature_share(
                destination="community/stable",
                package_id=package.package_id,
                store=store,
                runtime_schema=2,
                available_feature_ids=("DIST-001", "SOURCE-001"),
            )

    def test_import_tampered_package_fails_validation(self):
        package = build_package()
        store = MemoryShareStore()
        material = package.projection()
        material["package_id"] = "0" * 64
        payload = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        store.data[("community/stable", "0" * 64)] = payload
        with self.assertRaisesRegex(FeatureShareTransportError, "package_id"):
            import_feature_share(
                destination="community/stable",
                package_id="0" * 64,
                store=store,
                runtime_schema=2,
                available_feature_ids=("DIST-001", "SOURCE-001"),
            )

    def test_public_receipt_cannot_claim_activation_authority(self):
        package = build_package()
        store = MemoryShareStore()
        receipt = publish_feature_share(
            package.projection(), authorization=authorization(package.package_id), store=store
        )
        self.assertFalse(receipt.activation_authorized)
        self.assertFalse(receipt.source_mutation_authorized)
        self.assertFalse(receipt.install_authorized)


if __name__ == "__main__":
    unittest.main()
