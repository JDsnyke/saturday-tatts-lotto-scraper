import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class CIHygieneTests(unittest.TestCase):
    def test_one_off_self_modifying_ui_workflow_is_not_shipped(self):
        self.assertFalse((WORKFLOWS / "apply-ui-fixes.yml").exists())
        self.assertFalse((ROOT / ".github" / "scripts" / "apply_ui_fixes.py").exists())

    def test_ui_browser_gate_is_quiet_and_pr_scoped(self):
        workflow = (WORKFLOWS / "ui-browser.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertNotIn("branches: [fix/", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertIn("if: failure()", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)

    def test_browser_audit_is_self_validating(self):
        script = (ROOT / ".github" / "scripts" / "browser_audit.mjs").read_text(encoding="utf-8")
        self.assertIn("navigation failed", script)
        self.assertIn("visible skeleton", script)
        self.assertIn("horizontal overflow", script)
        self.assertIn("theme mismatch", script)
        self.assertIn("process.exitCode = 1", script)


if __name__ == "__main__":
    unittest.main()
