"""Regression contract for ordinary-user activation of MIRA shared-writer mode."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "workspace" / "apps_script" / "Code.gs"
WORKER = ROOT / "workspace" / "apps_script" / "CommandWorker.gs"


class SharedAccessMenuContractTests(unittest.TestCase):
    def test_sheet_menu_exposes_shared_access_without_apps_script_editor(self) -> None:
        code = CODE.read_text(encoding="utf-8")
        self.assertIn(
            ".addItem('Enable Android / shared access', 'miraEnableQueuedWriterFromMenu')",
            code,
        )
        self.assertIn("function miraEnableQueuedWriterFromMenu()", code)
        self.assertIn("const result = miraEnableQueuedWriter();", code)
        self.assertIn("MIRA shared access enabled", code)

    def test_menu_wrapper_reuses_the_existing_serialized_worker_activation(self) -> None:
        worker = WORKER.read_text(encoding="utf-8")
        self.assertIn("function miraEnableQueuedWriter()", worker)
        self.assertIn("miraEnsureCommandTrigger_();", worker)
        self.assertIn("MIRA_QUEUED_MODE_", worker)
        self.assertIn("LockService.getScriptLock()", worker)
        self.assertIn("everyMinutes(1)", worker)

    def test_default_user_surface_does_not_expose_internal_queued_writer_jargon(self) -> None:
        code = CODE.read_text(encoding="utf-8")
        menu_section = code[code.index("function onOpen()") : code.index("function miraInitializeCopy()")]
        self.assertNotIn("queued writer", menu_section.lower())
        self.assertNotIn("Apps Script", menu_section)


if __name__ == "__main__":
    unittest.main()
