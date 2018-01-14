from json import dumps, load, loads, JSONDecodeError
from os import path

from pygments import highlight, lexers, formatters

from robot.api import logger

from .keywords import Keywords


__version__ = '1.0.0.dev8'
user_agent =  "RESTinstance/{}".format(__version__)


class REST(Keywords):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, url,
                 ssl_verify=True,
                 accept="application/json, */*",
                 content_type="application/json",
                 user_agent=user_agent,
                 proxies={},
                 schema={},
                 spec=None):

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
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
        self.schema.update(REST._input_object(schema))
        self.spec = REST._input_string(spec)
        self.instances = []


    @staticmethod
    def print(json, header="", with_colors=True):
        json_data = dumps(json, ensure_ascii=False, indent=4)
        if with_colors:
            json_data = highlight(json_data,
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
            raise RuntimeError("Value {} is not a boolean".format(value))
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
            raise RuntimeError("Value {} is not an integer".format(value))
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
            raise RuntimeError("Value {} is not a number".format(value))
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
            raise RuntimeError("Value {} is not a string".format(value))
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
            raise RuntimeError("Value {} is not an object".format(value))
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
            raise RuntimeError("Value {} is not an array".format(value))
        return value

    @staticmethod
    def _input_json_file(path):
        try:
            with open(path) as file:
                return load(file)
        except IOError as e:
            raise RuntimeError("Error opening file '{}': {}".format(
                path, e))
        except JSONDecodeError as e:
            raise RuntimeError("Error loading JSON file '{}': {}".format(
                path, e))

    @staticmethod
    def _input_json_string(string):
        try:
            return loads(string)
        except ValueError as e:
            raise RuntimeError("Error parsing JSON: {}".format(e))

    @staticmethod
    def _input_non_string(value):
        try:
            return loads(dumps(value, ensure_ascii=False))
        except ValueError as e:
            raise RuntimeError("Error parsing value to JSON: {}".format(e))

    @staticmethod
    def _input_client_cert(value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError(
                    "Cert given as a Python list must have length of 2.")
            return value
        value = REST._input_json_string(value)
        if not isinstance(value, (str, list)):
            raise RuntimeError("Cert must be either a string or an array")
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError(
                    "Cert given as an array must have length of 2.")
        return value

    @staticmethod
    def _input_timeout(value):
        if isinstance(value, (int, float)):
            return [value, value]
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError(
                    "Timeout given as a Python list must have length of 2.")
            return value
        value = REST._input_json_string(value)
        if not isinstance(value, (int, float, list)):
            raise RuntimeError(
                "Timeout must be either an integer, a number or an array")
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError(
                    "Timeout given as an array must have length of 2.")
            else:
                return value
        return [value, value]
