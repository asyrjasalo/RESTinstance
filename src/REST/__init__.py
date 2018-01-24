from json import dumps, load, loads
from os import path

from pygments import highlight, lexers, formatters

from robot.api import logger

from .keywords import Keywords
from .version import __version__


class REST(Keywords):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, url,
                 ssl_verify=True,
                 accept="application/json, */*",
                 content_type="application/json",
                 user_agent="RESTinstance/{}".format(__version__),
                 proxies={},
                 schema={},
                 spec=None):

        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        if url.endswith('/'):
            url = url[:-1]
        self.url = url
        self.request = {
            'method': None,
            'endpoint': None,
            'query': {},
            'body': None,
            'headers': {
                'Accept': accept,
                'Content-Type': content_type,
                'User-Agent': user_agent
            },
            'proxies': REST._input_object(proxies),
            'timeout': None,
            'auth': [],
            'cert': None,
            'sslVerify': REST._input_boolean(ssl_verify),
            'allowRedirects': True
        }
        self.schema = {
            "exampled": True,
            "version": "draft04",
            "request": {},
            "response": {}
        }
        self.schema.update(self.input(schema))
        self.spec = self.input(spec)
        self.instances = []


    @staticmethod
    def print(json, header="", also_console=True):
        json = dumps(json, ensure_ascii=False, indent=4)
        logger.info("{}{}".format(header, json))    # no coloring for log.html
        if also_console:
            json_data = highlight(json,
                                  lexers.JsonLexer(),
                                  formatters.TerminalFormatter())
            logger.info("{}{}".format(header, json_data), also_console=True)
        return json

    @staticmethod
    def _input_boolean(value):
        if isinstance(value, bool):
            return value
        if path.isfile(value):
            value = REST._input_json_file(value)
        else:
            value = REST._input_json_string(value)
        if not isinstance(value, bool):
            raise RuntimeError("This expected value " +
                "is not a boolean:\n{}".format(value))
        return value

    @staticmethod
    def _input_integer(value):
        if isinstance(value, int):
            return value
        if path.isfile(value):
            value = REST._input_json_file(value)
        else:
            value = REST._input_json_string(value)
        if not isinstance(value, int):
            raise RuntimeError("This expected value " +
                "is not an integer:\n{}".format(value))
        return value

    @staticmethod
    def _input_number(value):
        if isinstance(value, float):
            return value
        if path.isfile(value):
            value = REST._input_json_file(value)
        else:
            value = REST._input_json_string(value)
        if not isinstance(value, float):
            raise RuntimeError("This expected value " +
                "is not a number:\n{}".format(value))
        return value

    @staticmethod
    def _input_string(value):
        if value == '""' or not value:
            return ""
        if not value.startswith('"'):
            value = '"' + value
        if not value.endswith('"'):
            value = value + '"'
        if path.isfile(value):
            value = REST._input_json_file(value)
        else:
            value = REST._input_json_string(value)
        if not isinstance(value, str):
            raise RuntimeError("This expected value " +
                "is not a string:\n{}".format(value))
        return value

    @staticmethod
    def _input_object(value):
        if isinstance(value, dict):
            return value
        if path.isfile(value):
            value = REST._input_json_file(value)
        else:
            value = REST._input_json_string(value)
        if not isinstance(value, dict):
            raise RuntimeError("This expected value " +
                "is not an object:\n{}".format(value))
        return value

    @staticmethod
    def _input_array(value):
        if isinstance(value, list):
            return value
        if path.isfile(value):
            value = REST._input_json_file(value)
        else:
            value = REST._input_json_string(value)
        if not isinstance(value, list):
            raise RuntimeError("This expected value " +
                "is not an array:\n{}".format(value))
        return value

    @staticmethod
    def _input_json_file(path):
        try:
            with open(path) as file:
                return load(file)
        except IOError as e:
            raise RuntimeError("File '{}' could not be opened:\n{}".format(
                path, e))
        except ValueError as e:
            raise RuntimeError("File '{}' is not valid JSON:\n{}".format(
                path, e))

    @staticmethod
    def _input_json_string(string):
        try:
            return loads(string)
        except ValueError:
            raise RuntimeError("This input is not valid JSON:\n{}".format(
                string))

    @staticmethod
    def _input_non_string(value):
        try:
            return loads(dumps(value, ensure_ascii=False))
        except ValueError:
            raise RuntimeError("This input is not valid JSON:\n{}".format(
                value))

    @staticmethod
    def _input_client_cert(value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This cert, given as a Python list, " +
                    "must have length of 2:\n{}".format(value))
            return value
        value = REST._input_json_string(value)
        if not isinstance(value, (str, list)):
            raise RuntimeError("This cert must be either " +
                "a string or an array:\n{}".format(value))
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This cert, given as an array, " +
                    "must have length of 2:\n{}".format(value))
        return value

    @staticmethod
    def _input_timeout(value):
        if isinstance(value, (int, float)):
            return [value, value]
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This timeout, given as a Python list, " +
                    "must have length of 2:\n{}".format(value))
            return value
        value = REST._input_json_string(value)
        if not isinstance(value, (int, float, list)):
            raise RuntimeError("This timeout must be either an integer, " +
                "a number or an array:\n{}".format(value))
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This timeout, given as an array, " +
                    "must have length of 2:\n{}".format(value))
            else:
                return value
        return [value, value]
