from io import open  # required for Python 2

from json import dumps, load, loads
from os import path

from pygments import highlight, lexers, formatters
from requests.packages.urllib3 import disable_warnings

from robot.api import logger

from .compat import STRING_TYPES
from .keywords import Keywords
from .version import __version__


class REST(Keywords):
    """Robot Framework test library for (RESTful) JSON APIs.

    RESTinstance validates JSON using JSON Schema, guiding you to write API tests
    basing on constraints (e.g. "response body property email must be a valid
    email") rather than on specific values (e.g. response body property email
    is "foo@bar.com"). This reduces test maintenance when values returned by
    the API are prone to change. Although validations do not require values,
    you can still use them whenever they make sense (e.g. GET response body
    from one endpoint, then POST some of its values to another endpoint).

    The library generates JSON Schema for requests and responses automatically,
    and the schema gets more accurate by your tests.
    This schema can be used as a documentation or a contract between
    different teams, or specialities (e.g. testers, developers), to agree on
    what kind of data the API handles. Additionally, you can mark validations
    to be skipped, and rather use the tests to define how the API should work,
    if the API does not exist yet - then the produced schema also acts as a
    design. The schema can be further used as a base for writing an OpenAPI
    specification, which RESTinstance can also test against (spec version 2.0,
    the support for 3.0, and generating also an OpenAPI spec automatically is
    planned).
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    # Altogether 24 keywords        context:
    # -----------------------------------------------------
    # 2 setting keywords            next instances
    # 4 expectation keywords        next instances
    # 7 request keywords            next instance
    # 8 assertion keywords          last instance's schema
    # 3 IO keywords                 see the respective KWs
    # -----------------------------------------------------

    def __init__(self, url,
                 ssl_verify=True,
                 accept="application/json, */*",
                 content_type="application/json",
                 user_agent="RESTinstance/%s" % (__version__),
                 proxies={},
                 schema={},
                 spec={},
                 instances=[]):

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
            'timeout': [None, None],
            'cert': None,
            'sslVerify': REST._input_boolean(ssl_verify),
            'allowRedirects': True
        }
        if not self.request['sslVerify']:
            disable_warnings()
        self.schema = {
            "exampled": True,
            "version": "draft04",
            "request": {},
            "response": {}
        }
        self.schema.update(self._input_object(schema))
        self.spec = {}
        self.spec.update(self._input_object(spec))
        self.instances = self._input_array(instances)


    @staticmethod
    def log_json(json, header="", also_console=True):
        json = dumps(json, ensure_ascii=False, indent=4)
        logger.info("%s%s" % (header, json))    # no coloring for log.html
        if also_console:
            json_data = highlight(json,
                                  lexers.JsonLexer(),
                                  formatters.TerminalFormatter())
            logger.info("%s%s" % (header, json_data), also_console=True)
        return json

    @staticmethod
    def _input_boolean(value):
        if isinstance(value, (bool)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (bool)):
                raise TypeError("This is not a Python boolean: %s" % (
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON boolean:\n%s" % (value))
        return json_value

    @staticmethod
    def _input_integer(value):
        if isinstance(value, (int)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (int)):
                raise TypeError("This is not a Python integer: %s" % (
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON integer:\n%s" % (value))
        return json_value

    @staticmethod
    def _input_number(value):
        if isinstance(value, (float)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (float)):
                raise TypeError("This is not a Python float: %s" % (
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON number:\n%s" % (value))
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
            if not isinstance(json_value, STRING_TYPES):
                raise TypeError("This is not a Python string: %s" % (
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON string:\n%s" % (value))
        return json_value

    @staticmethod
    def _input_object(value):
        if isinstance(value, (dict)):
            return value
        if path.isfile(value):
            json_value = REST._input_json_from_file(value)
        else:
            try:
                json_value = loads(value)
                if not isinstance(json_value, (dict)):
                    raise TypeError("This is not a Python dict: %s" % (
                        json_value))
            except (ValueError, TypeError):
                raise RuntimeError("This is neither a JSON object, " +
                "nor a path to an existing file:\n%s" % (value))
        return json_value

    @staticmethod
    def _input_array(value):
        if isinstance(value, (list)):
            return value
        if path.isfile(value):
            json_value = REST._input_json_from_file(value)
        else:
            try:
                json_value = loads(value)
                if not isinstance(json_value, (list)):
                    raise TypeError("This is not a Python list: %s" % (
                        json_value))
            except (ValueError, TypeError):
                raise RuntimeError("This is not a JSON array:\n%s" % (
                    value))
        return json_value

    @staticmethod
    def _input_json_from_file(path):
        try:
            with open(path, encoding="utf-8") as file:
                return load(file)
        except IOError as e:
            raise RuntimeError("File '%s' cannot be opened:\n%s" % (
                path, e))
        except ValueError as e:
            raise RuntimeError("File '%s' is not valid JSON:\n%s" % (
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
                "cannot be read as JSON:\n%s" % (value))

    @staticmethod
    def _input_client_cert(value):
        if isinstance(value, STRING_TYPES):
            return value
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError("This cert, given as a Python list, " +
                    "must have length of 2:\n%s" % (value))
            return value
        try:
            value = loads(value)
            if not isinstance(value, STRING_TYPES + (list)):
                raise TypeError("This is not a Python string " +
                    "or a list:\n%s" % (value))
        except (ValueError, TypeError):
            raise RuntimeError("This cert must be either " +
                "a JSON string or an array:\n%s" % (value))
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError("This cert, given as a JSON array, " +
                    "must have length of 2:\n%s" % (value))
        return value

    @staticmethod
    def _input_timeout(value):
        if isinstance(value, (int, float)):
            return [value, value]
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError("This timeout, given as a Python list, " +
                    "must have length of 2:\n%s" % (value))
            return value
        try:
            value = loads(value)
            if not isinstance(value, (int, float, list)):
                raise TypeError("This is not a Python integer, " +
                    "float or a list:\n%s" % (value))
        except (ValueError, TypeError):
            raise RuntimeError("This timeout must be either a JSON integer, " +
                "number or an array:\n%s" % (value))
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError("This timeout, given as a JSON array, " +
                    "must have length of 2:\n" % (value))
            else:
                return value
        return [value, value]
