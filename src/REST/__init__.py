# RESTinstance (https://github.com/asyrjasalo/RESTinstance)
# Robot Framework library for RESTful JSON APIs.
#
# Copyright(C) 2018- Anssi Syrjäsalo (http://a.syrjasalo.com)
# Licensed under GNU Lesser General Public License v3 (LGPL-3.0).

from io import open
from json import dumps, load, loads
from os import path
from urllib.parse import urlparse

from pygments import formatters, highlight, lexers
from requests.packages.urllib3 import disable_warnings
from robot.api import logger
from yaml import SafeLoader
from yaml import load as load_yaml

from .keywords import Keywords
from .version import __version__


class REST(Keywords):
    """RESTinstance is revolutionary and peaceful HTTP JSON API test library.

    It guides you to write more stable API tests relying on constraints (e.g. "people's email addresses must be valid"), rather than on values having the nature of change (e.g "the first created user's email is expected to stay foo@bar.com").

    It bases on observations that we are more often concerned whether and which properties changed, when they should (not) had as this signals a bug, and less often what the actual values were/are. This also helps in tackling tests failing only because the test environment data was (not) reset.

    These resolutions in mind, it walks the path with you to contract-driven testing, from automatically generated JSON Schema data models to having formal OpenAPI service specs, as the both are essentially of the same origin. Both are also supported by major forces (Google, Microsoft, IBM et al. founded OpenAPI Initiative), and are language-agnostic which goes as well with Robot Framework.

    Contracts represent a common language within software teams, recognising our differing talents as designers, developers and test experts; or perhaps your new business companion wants to integrate to the system as well, but there is still some noise in signal - yet you don't feel very content providing them the source code, let alone explaining technical details, like which JSON properties are must in the response body, over the phone.


    = Usage =

    For RESTful APIs, this library is intended to be used so that a test suite
    is dedicated per endpoint. The test suite is divided into test cases so that
    the differing operations (implemented by the endpoint via HTTP methods)
    are tested with separate test cases.


    = The state =

    The library represents its own state as JSON itself, as an array of objects.
    Together these objects are commonly called instances.

    A single instance always has these three properties:

    - Request data as a JSON object
    - Response data as a JSON object
    - JSON Schema for the above two properties

    For each request-response, as soon as the response has been gotten
    (and the request did not timeout), a new instance is created with these
    properties.

    Request and response schemas are inferred if they are not already
    expected by using expectation keywords. All the validations the library
    implements are based on JSON Schema [http://json-schema.org/draft-07/json-schema-validation.html|draft-07] by default
    but also [http://json-schema.org/draft-06/json-schema-validation.html|draft-06] and
    [http://json-schema.org/draft-04/json-schema-validation.html|draft-04] can be configured.

    = The scope =

    All the assertion keywords, `Output` and `Output Schema` are effective
    in the scope of the last instance.

    The scope of the library itself is test suite, meaning the instances
    are persisted in memory until the execution of the test suite is finished,
    regardless whether successfully or not.

    The last request and response is easiest seen with `Output`.
    The output is written to terminal by default, as this is usually faster
    for debugging purposes than finding the right keyword in ``log.html``.

    All instances can be output to a file with `RESTinstances` which can
    be useful for additional logging.

    = Known Issues =

    There is a [known issue](https://github.com/h2non/jsonpath-ng/issues/38) JSONPath parsing for keys with numerical values
    if the path is formatted as `$.element.1`. A workaround for this is to use the numerical value as `$.element['1']` instead.

    """

    ROBOT_LIBRARY_SCOPE = "TEST SUITE"

    # Altogether 24 keywords        context:
    # -------------------------------------------------------
    # 2 setting keywords            next instances
    # 3 expectation keywords        next instances
    # 7 operation keywords          next instance
    # 8 assertion keywords          last instance's schema
    # 4 I/O keywords                the last instance or none
    # -------------------------------------------------------

    def __init__(
        self,
        url=None,
        ssl_verify=True,
        accept="application/json, */*",
        content_type="application/json",
        user_agent="RESTinstance/%s" % (__version__),
        proxies={},
        schema={},
        spec={},
        instances=[],
        loglevel="WARN",
    ):
        self.request = {
            "method": None,
            "url": None,
            "scheme": "",
            "netloc": "",
            "path": "",
            "query": {},
            "body": None,
            "data": None,
            "auth": None,
            "headers": {
                "Accept": REST._input_string(accept),
                "Content-Type": REST._input_string(content_type),
                "User-Agent": REST._input_string(user_agent),
            },
            "proxies": REST._input_object(proxies),
            "timeout": [None, None],
            "cert": None,
            "sslVerify": REST._input_ssl_verify(ssl_verify),
            "allowRedirects": True,
        }
        if url:
            url = REST._input_string(url)
            if url.endswith("/"):
                url = url[:-1]
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            url_parts = urlparse(url)
            self.request["scheme"] = url_parts.scheme
            self.request["netloc"] = url_parts.netloc
            self.request["path"] = url_parts.path
        if not self.request["sslVerify"]:
            disable_warnings()
        self.schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": url,
            "description": None,
            "default": True,
            "examples": [],
            "type": "object",
            "properties": {
                "request": {"type": "object", "properties": {}},
                "response": {"type": "object", "properties": {}},
            },
        }
        self.schema.update(self._input_object(schema))
        self.spec = {}
        self.spec.update(self._input_object(spec))
        self.instances = self._input_array(instances)
        self.log_level = self._input_log_level(loglevel)
        self.auth = None

    @staticmethod
    def log_json(json, header="", also_console=True, sort_keys=False):
        json = dumps(
            json,
            ensure_ascii=False,
            indent=4,
            separators=(",", ": "),
            sort_keys=sort_keys,
        )
        logger.info(f"{header}\n{json}")  # no coloring for log.html
        if also_console:
            json_data = highlight(
                json, lexers.JsonLexer(), formatters.TerminalFormatter()
            )
            logger.console(f"{header}\n{json_data}", newline=False)
        return json

    @staticmethod
    def _input_boolean(value):
        if isinstance(value, (bool)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (bool)):
                raise RuntimeError("Input is not a JSON boolean: %s" % (value))
        except ValueError:
            raise RuntimeError("Input is not valid JSON: %s" % (value))
        return json_value

    @staticmethod
    def _input_integer(value):
        if isinstance(value, (int)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (int)):
                raise RuntimeError("Input is not a JSON integer: %s" % (value))
        except ValueError:
            raise RuntimeError("Input is not valid JSON: %s" % (value))
        return json_value

    @staticmethod
    def _input_number(value):
        if isinstance(value, (float, int)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (float, int)):
                raise RuntimeError("Input is not a JSON number: %s" % (value))
        except ValueError:
            raise RuntimeError("Input is not valid JSON: %s" % (value))
        return json_value

    @staticmethod
    def _input_string(value):
        if value == "":
            return ""
        if isinstance(value, str):
            if not value.startswith('"'):
                value = '"' + value
            if not value.endswith('"'):
                value = value + '"'
        try:
            json_value = loads(value)
            if not isinstance(json_value, str):
                raise RuntimeError("Input is not a JSON string: %s" % (value))
        except ValueError:
            raise RuntimeError("Input not is valid JSON: %s" % (value))
        return json_value

    @staticmethod
    def _input_object(value):
        if isinstance(value, (dict)):
            return value
        try:
            if path.isfile(value):
                json_value = REST._input_json_from_file(value)
            else:
                json_value = loads(value)
            if not isinstance(json_value, (dict)):
                raise RuntimeError(
                    "Input or file has no JSON object: %s" % (value)
                )
        except ValueError:
            raise RuntimeError(
                "Input is not valid JSON or a file: %s" % (value)
            )
        return json_value

    @staticmethod
    def _input_array(value):
        if isinstance(value, (list)):
            return value
        try:
            if path.isfile(value):
                json_value = REST._input_json_from_file(value)
            else:
                json_value = loads(value)
            if not isinstance(json_value, (list)):
                raise RuntimeError(
                    "Input or file has no JSON array: %s" % (value)
                )
        except ValueError:
            raise RuntimeError(
                "Input is not valid JSON or a file: %s" % (value)
            )
        return json_value

    @staticmethod
    def _input_json_from_file(path):
        try:
            with open(path, encoding="utf-8") as file:
                return load(file)
        except OSError as e:
            raise RuntimeError(f"File '{path}' cannot be opened:\n{e}")
        except ValueError as e:
            try:
                with open(path, encoding="utf-8") as file:
                    return load_yaml(file, Loader=SafeLoader)
            except ValueError:
                raise RuntimeError(
                    f"File '{path}' is not valid JSON or YAML:\n{e}"
                )

    @staticmethod
    def _input_json_as_string(string):
        return loads(string)

    @staticmethod
    def _input_json_from_non_string(value):
        try:
            return REST._input_json_as_string(dumps(value, ensure_ascii=False))
        except ValueError:
            raise RuntimeError("Input is not valid JSON: %s" % (value))

    @staticmethod
    def _input_client_cert(value):
        if value is None or value == "null":
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError(
                    "Client cert given as a (Python) list, "
                    + "must have length of 2: %s" % (value)
                )
            return value
        try:
            value = loads(value)
            if not isinstance(value, str + (list)):
                raise RuntimeError(
                    "Input is not a JSON string " + "or a list: %s" + (value)
                )
        except ValueError:
            raise RuntimeError(
                "Input is not a JSON string " + "or an array: %s " % (value)
            )
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError(
                    "Client cert given as a JSON array, "
                    + "must have length of 2: %s" % (value)
                )
        return value

    @staticmethod
    def _input_ssl_verify(value):
        try:
            return REST._input_boolean(value)
        except RuntimeError:
            value = REST._input_string(value)
            if not path.isfile(value):
                raise RuntimeError(
                    "SSL verify option is not "
                    + "a Python or a JSON boolean or a path to an existing "
                    + "CA bundle file: %s" % (value)
                )
            return value

    @staticmethod
    def _input_timeout(value):
        if isinstance(value, (int, float)):
            return [value, value]
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError(
                    "Timeout given as a (Python) list, "
                    + "must have length of 2: %s" % (value)
                )
            return value
        try:
            value = loads(value)
            if not isinstance(value, (int, float, list)):
                raise RuntimeError(
                    "Input is not a JSON integer, "
                    + "number or a list: %s" % (value)
                )
        except ValueError:
            raise RuntimeError("Input is not valid JSON: %s" % (value))
        if isinstance(value, (list)):
            if len(value) != 2:
                raise RuntimeError(
                    "Timeout given as a JSON array, "
                    + "must have length of 2: %s" % (value)
                )
            else:
                return value
        return [value, value]

    @staticmethod
    def _input_data(value):
        try:
            data = REST._input_object(value)
        except RuntimeError:
            if isinstance(value, bytes):
                data = value
            elif path.isfile(value):
                with open(value, "rb") as file:
                    data = file.read()
            else:
                raise RuntimeError(
                    "Data is not a dictionary, bytes, or path to a file"
                )
        return data

    @staticmethod
    def _input_log_level(loglevel):
        if loglevel.upper() not in (
            "TRACE",
            "DEBUG",
            "INFO",
            "HTML",
            "WARN",
            "ERROR",
        ):
            logger.warn(
                f"Unrecognized log level '{loglevel}'. Using default log level 'WARN'."
            )
            loglevel = "WARN"
        return loglevel.upper()
