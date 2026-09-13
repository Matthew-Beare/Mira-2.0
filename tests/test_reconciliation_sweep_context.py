import pytest

from ops.reconciliation_sweep import ManifestError, ModuleSpec, RunSpec


def test_non_text_context_is_rejected_as_manifest_error():
    with pytest.raises(ManifestError):
        RunSpec.build(
            local_date="2026-09-13",
            timezone="America/New_York",
            slot="am",
            context=42,
            modules=(ModuleSpec("finance"),),
        )
