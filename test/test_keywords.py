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

    def test_set_type_validations_string_pattern(self):
        self.library.schema = MagicMock()
        schema = {"type": "string"}
        self.library._set_type_validations("string", schema, {"pattern": "a+"})
        self.assertEqual(schema, {"type": "string", "pattern": "a+"})

    def test_set_type_validations_nullable(self):
        for type in ["string", "integer", "object", "number", "array"]:
            schema = {"type": type}
            self.library._set_type_validations(type, schema, {"nullable": True})
            self.assertEqual(schema, {"type": [type, "null"]})

    def test_set_type_validations_not_nullable(self):
        for type in ["string", "integer", "object", "number", "array"]:
            schema = {"type": type}
            self.library._set_type_validations(
                type, schema, {"nullable": False}
            )
            self.assertEqual(schema, {"type": type})

    def test_set_type_validations_no_validations(self):
        for validations in [None, {}]:
            for type in ["string", "integer", "object", "number", "array"]:
                schema = {"type": type}
                self.library._set_type_validations(type, schema, validations)
                self.assertEqual(schema, {"type": type})

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

    def test_set_headers_with_long_bearer_token(self):
        """Test that Set Headers handles long bearer tokens without raising OSError.

        This test reproduces the issue where a long bearer token (longer than
        filesystem filename limits) would cause OSError: [Errno 36] File name too long
        when the code tried to check if the value was a file path.
        """
        # Create a very long bearer token (300+ characters, exceeding typical
        # filesystem filename limits of 255 bytes)
        long_token = "Bearer " + "x" * 300
        headers = {"Authorization": long_token}

        # This should not raise OSError
        result = self.library.set_headers(headers)

        # Verify the header was set correctly
        self.assertEqual(
            self.library.request["headers"]["Authorization"], long_token
        )
        self.assertIn("Authorization", result)

    def test_set_headers_with_long_json_string(self):
        """Test that Set Headers handles long JSON strings without raising OSError."""
        # Create a JSON string with a very long value (300+ characters)
        long_value = "x" * 300
        headers_json = f'{{"Authorization": "Bearer {long_value}"}}'

        # This should not raise OSError
        result = self.library.set_headers(headers_json)

        # Verify the header was set correctly
        self.assertIn("Authorization", result)
        self.assertTrue(result["Authorization"].startswith("Bearer"))

    def test_input_object_with_long_string(self):
        """Test that _input_object handles long strings without raising OSError."""
        # Create a very long JSON string (300+ characters)
        long_json = '{"key": "' + "x" * 300 + '"}'

        # This should not raise OSError
        result = REST.REST._input_object(long_json)

        # Verify it was parsed as JSON
        self.assertIsInstance(result, dict)
        self.assertIn("key", result)
        self.assertEqual(len(result["key"]), 300)

    def test_input_array_with_long_string(self):
        """Test that _input_array handles long strings without raising OSError."""
        # Create a very long JSON array string (300+ characters)
        long_json = '["' + "x" * 300 + '"]'

        # This should not raise OSError
        result = REST.REST._input_array(long_json)

        # Verify it was parsed as JSON
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 300)
