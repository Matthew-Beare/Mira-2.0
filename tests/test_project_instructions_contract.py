from pathlib import Path


INSTRUCTIONS = Path("PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")


def test_native_host_connection_contract_is_durable() -> None:
    required = (
        "ORDINARY-USER CONNECTION EXECUTION",
        "ordinary language",
        "current host discovery",
        "Surface the native install/connect/authorization control directly",
        "successful OAuth or app-connect screen alone is not sufficient evidence for `Connected`",
        "Connecting Calendar must not silently activate Gmail, Drive",
        "fail honestly without substituting another provider",
    )
    for phrase in required:
        assert phrase in INSTRUCTIONS


def test_default_personal_does_not_export_provider_engineering_to_user() -> None:
    required = (
        "settings hunt",
        "OAuth scopes",
        "resource IDs",
        "developer-console steps",
        "terminal work",
    )
    for phrase in required:
        assert phrase in INSTRUCTIONS


def test_scheduled_runtime_does_not_require_local_checkout() -> None:
    required = (
        "SCHEDULED RUNTIME PORTABILITY",
        "must not assume that a repository checkout",
        "platform trigger is authoritative",
        "platform/runtime system clock",
        "its absence alone must not circuit-break",
        "Independent modules should continue when another module fails",
    )
    for phrase in required:
        assert phrase in INSTRUCTIONS
