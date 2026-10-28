import io
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ai.llm_client import LLMClient
from core.executor import Executor


class TestLLMClient(unittest.TestCase):
    def test_gemini_uses_configured_model_and_parses_json(self):
        expected = {
            "batch_script": "@echo off",
            "manifest": {"applications": []},
        }
        mock_openai = types.ModuleType("openai")
        mock_client = Mock()
        mock_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content=json.dumps(expected)))
        ]
        mock_openai.OpenAI = Mock(return_value=mock_client)

        with (
            patch.dict(
                "os.environ",
                {
                    "LLM_PROVIDER": "gemini",
                    "GEMINI_API_KEY": "test-key",
                    "GEMINI_MODEL": "gemini-3.8-flash",
                },
                clear=True,
            ),
            patch.dict(sys.modules, {"openai": mock_openai}),
        ):
            result = LLMClient().generate_plan("Install Git")

        self.assertEqual(result, expected)
        mock_openai.OpenAI.assert_called_once_with(
            api_key="test-key",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=60.0,
            max_retries=5,
        )
        mock_client.chat.completions.create.assert_called_once()
        self.assertEqual(
            mock_client.chat.completions.create.call_args.kwargs["model"],
            "gemini-3.8-flash",
        )

    def test_gemini_errors_include_status_and_sanitized_details(self):
        class ApiError(Exception):
            status_code = 404

        mock_openai = types.ModuleType("openai")
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = ApiError(
            "API error: model unavailable; key=test-key"
        )
        mock_openai.OpenAI = Mock(return_value=mock_client)

        with (
            patch.dict(
                "os.environ",
                {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"},
                clear=True,
            ),
            patch.dict(sys.modules, {"openai": mock_openai}),
        ):
            with self.assertRaisesRegex(RuntimeError, "HTTP 404") as context:
                LLMClient().generate_plan("Install Git")
        self.assertNotIn("test-key", str(context.exception))
        self.assertIn("key=[REDACTED]", str(context.exception))

    def test_gemini_503_reports_temporary_unavailability_and_retries(self):
        class ApiError(Exception):
            status_code = 503

        mock_openai = types.ModuleType("openai")
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = ApiError(
            "This model is currently experiencing high demand."
        )
        mock_openai.OpenAI = Mock(return_value=mock_client)

        with (
            patch.dict(
                "os.environ",
                {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"},
                clear=True,
            ),
            patch.dict(sys.modules, {"openai": mock_openai}),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "temporarily overloaded.*wait briefly and try again",
            ):
                LLMClient().generate_plan("Install Git")

        mock_openai.OpenAI.assert_called_once_with(
            api_key="test-key",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=60.0,
            max_retries=5,
        )

    def test_missing_gemini_key_uses_local_planner(self):
        with patch.dict(
            "os.environ",
            {"LLM_PROVIDER": "gemini"},
            clear=True,
        ):
            client = LLMClient()
            self.assertFalse(client.is_configured())
            self.assertEqual(
                client.generate_plan("Install Git")["manifest"]["applications"][0]["package_id"],
                "Git.Git",
            )

    def test_local_planner_supports_broader_software_names(self):
        with patch.dict("os.environ", {"LLM_PROVIDER": "gemini"}, clear=True):
            client = LLMClient()
            result = client.generate_plan("Install Firefox, Krita, and Inkscape")

        package_ids = [app["package_id"] for app in result["manifest"]["applications"]]
        self.assertIn("Mozilla.Firefox", package_ids)
        self.assertIn("Krita.Krita", package_ids)
        self.assertIn("Inkscape.Inkscape", package_ids)

    def test_existing_openai_key_keeps_openai_as_default_provider(self):
        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": "existing-key"},
            clear=True,
        ):
            client = LLMClient()

        self.assertEqual(client.provider, "openai")
        self.assertTrue(client.is_configured())

    def test_retired_gemini_25_flash_setting_is_migrated(self):
        with patch.dict(
            "os.environ",
            {
                "LLM_PROVIDER": "gemini",
                "GEMINI_API_KEY": "test-key",
                "GEMINI_MODEL": "gemini-2.5-flash",
            },
            clear=True,
        ):
            client = LLMClient()

        self.assertEqual(client.gemini_model, "gemini-3.8-flash")

    def test_executor_streams_live_progress_output(self):
        process = Mock()
        process.stdout = io.StringIO("Downloading package...\nProgress: 32%\nInstallation complete\n")
        process.wait.return_value = 0
        process.poll.return_value = 0

        with patch("subprocess.Popen", return_value=process) as mocked_popen:
            executor = Executor(Path("output/runs/test"))
            messages = []
            exit_code = executor.run_batch_script(Path("installer.bat"), stream_callback=messages.append)

        self.assertEqual(exit_code, 0)
        self.assertTrue(any("Progress: 32%" in line for line in messages))
        mocked_popen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
