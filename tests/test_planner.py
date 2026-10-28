import unittest
from unittest.mock import Mock

from ai.prompts import SYSTEM_PROMPT
from core.planner import Planner


class TestPlanner(unittest.TestCase):
    def test_prompt_keeps_installation_separate_from_unsupported_configuration(self):
        self.assertIn("do not omit an", SYSTEM_PROMPT.lower())
        self.assertIn("installation just because", SYSTEM_PROMPT.lower())
        self.assertIn("database accounts, database passwords, or root credentials", SYSTEM_PROMPT)
        self.assertNotIn("using its exact Winget package ID", SYSTEM_PROMPT)

    def test_error_suggests_natural_language_prompt(self):
        planner = Planner()
        planner.llm = Mock()
        planner.llm.generate_plan.return_value = {
            "batch_script": "@echo off\necho No applications requested.",
            "manifest": {"applications": [], "configuration": {}},
        }

        with self.assertRaisesRegex(ValueError, "Try a prompt focused on installation") as context:
            planner.generate("Install MySQL and configure an account")

        self.assertNotIn("using its exact Winget package ID", str(context.exception))

    def test_empty_ai_plan_returns_actionable_error(self):
        planner = Planner()
        planner.llm = Mock()
        planner.llm.generate_plan.return_value = {
            "batch_script": "@echo off\necho No applications requested.",
            "manifest": {
                "applications": [],
                "configuration": {},
                "manual_steps": ["Database password configuration is unsupported."],
            },
        }

        with self.assertRaisesRegex(
            ValueError,
            "Try a prompt focused on installation",
        ) as context:
            planner.generate("Install MySQL and configure an account")

        self.assertIn("database credential setup is unsupported", str(context.exception))


if __name__ == "__main__":
    unittest.main()
