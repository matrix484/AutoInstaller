import unittest

from core.validator import Validator


class TestValidator(unittest.TestCase):
    def test_valid_batch_script(self):
        script = """@echo off
        title Auto Installer
        winget install --id Git.Git --exact --silent --accept-package-agreements --accept-source-agreements
        if errorlevel 1 exit /b 1
        """
        result = Validator.validate_batch_script(script)
        self.assertTrue(result.is_valid)

    def test_accepts_explicit_errorlevel_variable_guard(self):
        script = """@echo off
        winget install --id Oracle.MySQL --exact --silent --accept-package-agreements --accept-source-agreements
        if %errorlevel% neq 0 exit /b %errorlevel%
        """
        result = Validator.validate_batch_script(script)
        self.assertTrue(result.is_valid, result.errors)

    def test_rejects_unapproved_errorlevel_command(self):
        script = """@echo off
        winget install --id Oracle.MySQL --exact --silent --accept-package-agreements --accept-source-agreements
        if %errorlevel% neq 0 del /s C:\\temp
        """
        result = Validator.validate_batch_script(script)
        self.assertFalse(result.is_valid)

    def test_invalid_batch_script_rejects_power_shell(self):
        script = "powershell -ExecutionPolicy Bypass -File installer.ps1"
        result = Validator.validate_batch_script(script)
        self.assertFalse(result.is_valid)

    def test_invalid_manifest_missing_applications(self):
        manifest = {"configuration": {}}
        result = Validator.validate_manifest(manifest)
        self.assertFalse(result.is_valid)

    def test_empty_applications_explains_unsupported_database_configuration(self):
        manifest = {"applications": [], "configuration": {}}
        result = Validator.validate_manifest(manifest)
        self.assertFalse(result.is_valid)
        self.assertIn("database account and password", result.errors[0])

    def test_invalid_package_id_rejected(self):
        manifest = {"applications": [{"name": "test", "package_id": "bad id"}]}
        result = Validator.validate_manifest(manifest)
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
