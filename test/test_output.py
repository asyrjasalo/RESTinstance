import io
import os
import re
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

from src import REST


class TestOutputLogJsonCalling(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dict = {"robotframework": "cool"}
        self.output_schema_dict = {
            "properties": {"robotframework": {"type": "string"}},
            "required": ["robotframework"],
            "type": "object",
        }
        self.library = REST.REST()
        self.library.log_json = MagicMock()
        return super().setUp()

    def test_output_log_json_default(self):
        self.library.output(self.output_dict)
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=False, also_console=True
        )

    def test_output_log_json_console_true(self):
        self.library.output(self.output_dict, also_console=True)
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=False, also_console=True
        )

    def test_output_log_json_console_false(self):
        self.library.output(self.output_dict, also_console=False)
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=False, also_console=False
        )

    def test_output_log_json_sort_keys_false(self):
        self.library.output(self.output_dict, sort_keys=False)
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=False, also_console=True
        )

    def test_output_log_json_sort_keys_true(self):
        self.library.output(self.output_dict, sort_keys=True)
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=True, also_console=True
        )

    def test_output_string_values_true(self):
        self.library.output(self.output_dict, also_console="true")
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=False, also_console=True
        )

    def test_output_string_values_false(self):
        self.library.output(self.output_dict, also_console="false")
        self.library.log_json.assert_called_with(
            self.output_dict, sort_keys=False, also_console=False
        )

    def test_output_schema_log_json_default(self):
        self.library.output_schema(self.output_dict)
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=False, also_console=True
        )

    def test_output_schema_log_json_console_true(self):
        self.library.output_schema(self.output_dict, also_console=True)
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=False, also_console=True
        )

    def test_output_schema_log_json_console_false(self):
        self.library.output_schema(self.output_dict, also_console=False)
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=False, also_console=False
        )

    def test_output_schema_log_json_sort_keys_false(self):
        self.library.output_schema(self.output_dict, sort_keys=False)
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=False, also_console=True
        )

    def test_output_schema_log_json_sort_keys_true(self):
        self.library.output_schema(self.output_dict, sort_keys=True)
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=True, also_console=True
        )

    def test_output_schema_string_values_true(self):
        self.library.output_schema(self.output_dict, also_console="true")
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=False, also_console=True
        )

    def test_output_schema_string_values_false(self):
        self.library.output_schema(self.output_dict, also_console="false")
        self.library.log_json.assert_called_with(
            self.output_schema_dict, sort_keys=False, also_console=False
        )


class OutputConsoleHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dict = {"robotframework": "cool"}
        self.output_console = '\n{\n    "robotframework": "cool"\n}\n'
        self.output_console_file = '{\n    "robotframework": "cool"\n}'

        self.output_schema_dict = {
            "properties": {"robotframework": {"type": "string"}},
            "required": ["robotframework"],
            "type": "object",
        }
        self.output_schema_console = """
{
    "type": "object",
    "properties": {
        "robotframework": {
            "type": "string"
        }
    },
    "required": [
        "robotframework"
    ]
}
"""
        self.output_schema_file = """{
    "type": "object",
    "properties": {
        "robotframework": {
            "type": "string"
        }
    },
    "required": [
        "robotframework"
    ]
}"""

        self.original = sys.__stdout__
        sys.__stdout__ = self.log_buf = io.StringIO()
        self.library = REST.REST()
        return super().setUp()

    def tearDown(self):
        sys.__stdout__ = self.original

    def _remove_ansi(self, text):
        """Remove ANSI codes from text"""
        ansi_escape = re.compile(
            r"""
                \x1B  # ESC
                (?:   # 7-bit C1 Fe (except CSI)
                    [@-Z\\-_]
                |     # or [ for CSI, followed by a control sequence
                    \[
                    [0-?]*  # Parameter bytes
                    [ -/]*  # Intermediate bytes
                    [@-~]   # Final byte
                )
            """,
            re.VERBOSE,
        )
        return ansi_escape.sub("", text)


class TestOutputConsole(OutputConsoleHelpers):
    def test_output_default(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output(self.output_dict)
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, self.output_console)
        mock_log.assert_not_called()

    def test_output_default_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output(self.output_dict, also_console=True)
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, self.output_console)
        mock_log.assert_not_called()

    def test_output_default_no_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output(self.output_dict, also_console=False)
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, "")
        mock_log.assert_not_called()

    def test_output_file_and_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output(self.output_dict, file_path="rest.log")
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, self.output_console)
        mock_log.assert_called_with(
            f"{os.getcwd()}/rest.log", "w", encoding="utf-8"
        )
        handle = mock_log()
        handle.write.assert_called_once_with(self.output_console_file)

    def test_output_file_and_no_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output(
                self.output_dict, file_path="rest.log", also_console=False
            )
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, "")
        mock_log.assert_called_with(
            f"{os.getcwd()}/rest.log", "w", encoding="utf-8"
        )
        handle = mock_log()
        handle.write.assert_called_once_with(self.output_console_file)


class TestOutputSchemaConsole(OutputConsoleHelpers):
    def test_output_schema_default(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output_schema(self.output_dict)
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, self.output_schema_console)
        mock_log.assert_not_called()

    def test_output_schema_default_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output_schema(self.output_dict, also_console=True)
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, self.output_schema_console)
        mock_log.assert_not_called()

    def test_output_schema_default_no_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output_schema(self.output_dict, also_console=False)
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, "")
        mock_log.assert_not_called()

    def test_output_schema_file_and_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output_schema(self.output_dict, file_path="rest.log")
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, self.output_schema_console)
        mock_log.assert_called_with(
            f"{os.getcwd()}/rest.log", "w", encoding="utf-8"
        )
        handle = mock_log()
        handle.write.assert_called_once_with(self.output_schema_file)

    def test_output_schema_file_and_no_console(self):
        mock_log = mock_open()
        with patch("src.REST.keywords.open", mock_log, create=True):
            self.library.output_schema(
                self.output_dict, file_path="rest.log", also_console=False
            )
        log_clean = self._remove_ansi(self.log_buf.getvalue())
        self.assertEqual(log_clean, "")
        mock_log.assert_called_with(
            f"{os.getcwd()}/rest.log", "w", encoding="utf-8"
        )
        handle = mock_log()
        handle.write.assert_called_once_with(self.output_schema_file)
