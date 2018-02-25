from json import dumps, load, loads
from os import path

from pygments import highlight, lexers, formatters
from requests.packages.urllib3 import disable_warnings

from robot.api import logger

from .keywords import Keywords
from .version import __version__


class REST(Keywords):
    """Robot Framework test library for (RESTful) JSON APIs.

    = Why? =

    1. RESTinstance benefits from Robot Framework's language-agnostic, keyword
    driven syntax for API tests. As with Robot Framework, using it is not tied
    to any programming language nor development framework.
    RESTinstance rather keeps things simple and the language humane, also for
    the testers without programming knowledge. It builts on long-term
    technologies, that have already established communities, such as HTTP,
    JSON (Schema), OpenAPI and Robot Framework.

    2. It validates JSON using JSON Schema, directing you to write API tests
    based on constraints (e.g. "response body property email must be a valid
    email"), rather than on specific values (e.g. response body property email
    is "foo@bar.com"). This reduces test maintenance when the values returned by
    the API are prone to change. Although validations require no values,
    you can still have them whenever they are relevant (e.g. GET response body
    from one endpoint, then POST some of its properties to another endpoint).

    3. It generates JSON Schema for requests and responses automatically,
    and this schema gets more accurate when you write the tests.
    This schema can be used as a documentation or even a contract between
    different teams or specialities (e.g. testers, developers) to agree on
    what kind of data the API handles. Additionally, you can mark validations
    to be skipped and rather use the tests to define how the API should work,
    if it does not exist yet - then the produced schema is also the design.
    The schema can be further used as a base for writing OpenAPI specification,
    which RESTinstance can also test against (version 2.0, the support for 3.0
    and generating also OpenAPI spec automatically is planned).


    = Installation =

    == Python installation ==

    pip install --upgrade RESTinstance

    == Docker installation ==

    If you have Docker available, see
    [rfdocker](https://github.com/asyrjasalo/rfdocker).
    Basically, download `Dockerfile` and `rfdocker` from that repository,
    add `RESTinstance` into `requirements.txt` and comment out the
    requirements.txt installation line in `Dockerfile`. That's it.
    Then run your tests with `./rfdocker` - no Python packages
    are installed on the host, and there is no risk of conflicting packages.


    = Usage =

    See keyword documentation for all the keywords.

    The library covers (at least) three kind of API tests.

    These are best demonstrated with examples below:

    1. Testing for JSON types and formats using JSON Schema validations

    For examples, see tests/validations.robot

    2. Flow-driven API tests, i.e. multiple APIs are called for the end result

    For examples, see tests/methods.robot

    3. Testing API requests and responses against a schema or a specifaction

    For examples testing against JSON schemas, see tests/schema.robot

    For examples testing against Swagger 2.0 spec, see tests/spec.robot


    = Development ==

    The issues and feature requests are tracked in GitHub issue tracker.

    We kindly do take pull requests. Please mention if you do not want your
    name listed in contributors.

    == Run library's own tests ==

    Docker is preferred for devenv and running the library's own tests.

    To start the test API and run the tests:

    ./test

    == Test API ==

    This system under test is implemented by
    [mounterest](https://github.com/asyrjasalo/mounterest),
    which in turn bases on [mountebank](http://www.mbtest.org).

    In the scope of this library's tests, mounterest acts as a HTTP proxy to
    [Typicode's live JSON server](jsonplaceholder.typicode.com) and uses
    mountebank's injections to enrich the responses from there slightly,
    so that they better match to this library's testing needs.

    Particularly, the injectors bundled in mounterest allow us to test
    the library also with non-safe HTTP methods (POST, PUT, PATCH, DELETE).
    Otherwise they would have no effect, as the live server is read-only.

    These injectors share a state and intercept non-safe HTTP requests,
    mimicking their changes in the state only, instead of trying to do
    them on the live-server. This state is cleared between the test runs.

    You may benefit from mounterest for your own purposes, if you are
    e.g. lacking a test environment where you can make changes.
    The tool is under active development but outside the scope of this library.
    See [GitHub repository](https://github.com/asyrjasalo/mounterest) for more.


    = Credits =

    RESTinstance is licensed under Apache License 2.0.

    RESTinstance was originally written by Anssi Syrjäsalo, and was initially
    presented at [RoboCon 2018](https://robocon.io), in Helsinki, Finland.

    RESTinstance 1.0.0 was released at 2018-03-01.


    == Libraries ==

In addition to Robot Framework, RESTinstance uses the following (excellent!)
Python tools under the hood:

- [GenSON](https://github.com/wolverdude/GenSON), by Jon "wolverdude" Wolverton,
  for JSON Schema generation
- [Flex](https://github.com/pipermerriam/flex), by Piper Merriam,
  for Swagger 2.0 validation
- [jsonschema](https://github.com/Julian/jsonschema), by Julian Berman,
  for JSON Schema draft-04 validation
- [requests](https://github.com/requests/requests), by Kenneth Reitz,
  for HTTP requests

See requirements.txt for a list of all the (direct) dependencies.


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
                 user_agent="RESTinstance/{}".format(__version__),
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
