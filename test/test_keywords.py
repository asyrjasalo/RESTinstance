import unittest
from unittest.mock import MagicMock

from src import REST


class TestKeywords(unittest.TestCase):
    def setUp(self) -> None:
        self.library = REST.REST()
        return super().setUp()

    def test_set_ssl_verify(self):
        self.assertTrue(self.library.request["sslVerify"])
        self.library.set_ssl_verify(False)
        self.assertFalse(self.library.request["sslVerify"])

    def test_set_log_level(self):
        self.assertEqual(self.library.log_level, "WARN")
        self.library.set_log_level("INFO")
        self.assertEqual(self.library.log_level, "INFO")
        self.library.set_log_level("NOT ACCEPTABLE")
        self.assertEqual(self.library.log_level, "WARN")

    def test_find_by_field(self):
        instance = {"schema": {"properties": "abba"}}
        self.library._find_by_path = MagicMock()
        self.library.instances.append(instance)
        observed = self.library._find_by_field("abba")
        self.library._find_by_path.assert_called_with(
            "abba", ["abba"], {"schema": {"properties": "abba"}}, "abba", True
        )
        self.assertTrue(isinstance(observed, list))

    def test_find_by_field_startingwith_dollar(self):
        self.library._last_instance_or_error = MagicMock()
        self.library._last_instance_or_error.return_value = {
            "response": {"body": {"abba": ["abba"]}},
            "schema": {
                "properties": {
                    "response": {"properties": {"body": {"abba": ["abba"]}}}
                }
            },
        }
        self.library._find_by_path = MagicMock()
        observed = self.library._find_by_field("$.abba[:1]")
        self.library._find_by_path.assert_called_with(
            "$.abba[:1]",
            ["abba", "0"],
            {"abba": ["abba"]},
            {"abba": ["abba"]},
            True,
        )
        self.assertTrue(isinstance(observed, list))

    def test_find_by_field_numerical_value(self):
        self.library._last_instance_or_error = MagicMock()
        self.library._last_instance_or_error.return_value = {
            "response": {
                "body": {"element": {"1": "first", "2": "second", "3": "third"}}
            },
            "schema": {
                "properties": {
                    "response": {"properties": {"body": {"1": "first"}}}
                }
            },
        }
        observed = self.library._find_by_field("$.element['1']")
        expected = [
            {
                "path": ["element", "1"],
                "reality": "first",
                "schema": {"type": "string"},
            }
        ]
        self.assertEqual(observed, expected)
        with self.assertRaises(RuntimeError):
            self.library._find_by_field("$.element.1")

    def test_find_by_field_with_dollar(self):
        self.library._last_instance_or_error = MagicMock()
        self.library._last_instance_or_error.return_value = {
            "response": {"body": "test"},
            "schema": {
                "properties": {"response": {"properties": {"body": "test"}}}
            },
        }
        expected = [
            {"path": ["response", "body"], "reality": "test", "schema": "test"}
        ]
        observed = self.library._find_by_field("$")
        self.assertEqual(observed, expected)

    def test_find_by_field_without_existing_schema(self):
        self.assertRaises(AssertionError, self.library._find_by_field, "abba")

    def test_find_by_field_raises_runtime_error_with_invalid_query(self):
        self.library._last_instance_or_error = MagicMock()
        self.library._last_instance_or_error.return_value = {
            "response": {"body": {"abba": ["abba"]}},
            "schema": {
                "properties": {
                    "response": {"properties": {"body": {"abba": ["abba"]}}}
                }
            },
        }
        self.library._find_by_path = MagicMock()
        self.assertRaises(RuntimeError, self.library._find_by_field, "$abba13")
