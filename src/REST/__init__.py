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
                 spec={}):

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
        self.schema.update(self._input_object(schema))
        self.spec = self._input_noneness_or_object(spec)
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
        try:
            json_value = loads(value)
            if not isinstance(json_value, bool):
                raise TypeError("This is not a Python boolean: {}".format(
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON boolean:\n{}".format(value))
        return json_value

    @staticmethod
    def _input_integer(value):
        if isinstance(value, int):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, int):
                raise TypeError("This is not a Python integer: {}".format(
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON integer:\n{}".format(value))
        return json_value

    @staticmethod
    def _input_number(value):
        if isinstance(value, float):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, float):
                raise TypeError("This is not a Python float: {}".format(
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON number:\n{}".format(value))
        return json_value

    @staticmethod
    def _input_string(value):
        if value == '""' or not value:
            return ""
        if not value.startswith('"'):
            value = '"' + value
        if not value.endswith('"'):
            value = value + '"'
        try:
            json_value = loads(value)
            if not isinstance(json_value, str):
                raise TypeError("This is not a Python string: {}".format(
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON string:\n{}".format(value))
        return json_value

    @staticmethod
    def _input_object(value):
        if isinstance(value, dict):
            return value
        if path.isfile(value):
            json_value = REST._input_json_from_file(value)
        else:
            try:
                json_value = loads(value)
                if not isinstance(json_value, dict):
                    raise TypeError("This is not a Python dict: {}".format(
                        json_value))
            except (ValueError, TypeError):
                raise RuntimeError("This is neither a JSON object, " +
                "nor a path to an existing file:\n{}".format(value))
        return json_value

    @staticmethod
    def _input_array(value):
        if isinstance(value, list):
            return value
        if path.isfile(value):
            json_value = REST._input_json_from_file(value)
        else:
            try:
                json_value = loads(value)
                if not isinstance(json_value, list):
                    raise TypeError("This is not a Python list: {}".format(
                        json_value))
            except (ValueError, TypeError):
                raise RuntimeError("This is not a JSON array:\n{}".format(
                    value))
        return json_value

    @staticmethod
    def _input_noneness_or_object(value):
        if value is None:
            return None
        if isinstance(value, str) and value.lower() == "null":
            return None
        return REST._input_object(value)

    @staticmethod
    def _input_json_from_file(path):
        try:
            with open(path) as file:
                return load(file)
        except IOError as e:
            raise RuntimeError("File '{}' cannot be opened:\n{}".format(
                path, e))
        except ValueError as e:
            raise RuntimeError("File '{}' is not valid JSON:\n{}".format(
                path, e))

    @staticmethod
    def _input_json_as_string(string):
        return loads(string)

    @staticmethod
    def _input_json_from_non_string(value):
        try:
            return REST._input_json_as_string(dumps(value, ensure_ascii=False))
        except ValueError:
            raise RuntimeError("This Python value " +
                "cannot be read as JSON:\n{}".format(value))

    @staticmethod
    def _input_client_cert(value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This cert, given as a Python list, " +
                    "must have length of 2:\n{}".format(value))
            return value
        try:
            value = loads(value)
            if not isinstance(value, (str, list)):
                raise TypeError("This is not a Python string " +
                    "or a list:\n{}".format(value))
        except (ValueError, TypeError):
            raise RuntimeError("This cert must be either " +
                "a JSON string or an array:\n{}".format(value))
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This cert, given as a JSON array, " +
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
        try:
            value = loads(value)
            if not isinstance(value, (int, float, list)):
                raise TypeError("This is not a Python integer, " +
                    "float or a list:\n{}".format(value))
        except (ValueError, TypeError):
            raise RuntimeError("This timeout must be either a JSON integer, " +
                "number or an array:\n{}".format(value))
        if isinstance(value, list):
            if len(value) != 2:
                raise RuntimeError("This timeout, given as a JSON array, " +
                    "must have length of 2:\n{}".format(value))
            else:
                return value
        return [value, value]
