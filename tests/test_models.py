import unittest

from core.models import AppRequest, RunResult, ValidationResult


class TestModels(unittest.TestCase):
    def test_app_request_defaults(self):
        request = AppRequest(prompt="Install Git")
        self.assertEqual(request.prompt, "Install Git")
        self.assertEqual(request.package_ids, [])

    def test_validation_result(self):
        result = ValidationResult(True, ["warning"], [])
        self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()
