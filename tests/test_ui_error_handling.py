import unittest
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

from ui.main_window import App


class TestWorkflowErrorHandling(unittest.TestCase):
    def test_error_message_is_available_when_tk_callbacks_run(self):
        app = App.__new__(App)
        app.root = SimpleNamespace(after=lambda delay, callback: callback())
        app.set_status = Mock()
        app.append_log = Mock()
        app.summary_box = Mock()

        app._show_workflow_error("API request failed")

        app.set_status.assert_called_once_with("Error")
        app.append_log.assert_called_once_with("ERROR: API request failed")
        app.summary_box.insert.assert_called_once_with(
            "1.0", "Error: API request failed"
        )
        app.summary_box.configure.assert_any_call(state="normal")
        app.summary_box.configure.assert_any_call(state="disabled")

    def test_open_output_dir_creates_missing_folder_before_opening(self):
        app = App.__new__(App)
        app.append_log = Mock()

        with tempfile.TemporaryDirectory() as temp_dir:
            app.run_dir = Path(temp_dir) / "output" / "runs"

            with patch("ui.main_window.os.startfile", create=True) as startfile:
                app.open_output_dir()

            self.assertTrue(app.run_dir.is_dir())
            startfile.assert_called_once_with(str(app.run_dir))


if __name__ == "__main__":
    unittest.main()
