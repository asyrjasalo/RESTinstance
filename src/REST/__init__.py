#  Copyright 2018-  Anssi Syrjäsalo
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# For Python 2
from __future__ import unicode_literals
from __future__ import division
from io import open
from .compat import IS_PYTHON_2, STRING_TYPES

from json import dumps, load, loads
from os import path
from yaml import load as load_yaml

from pygments import highlight, lexers, formatters
from requests.packages.urllib3 import disable_warnings

if IS_PYTHON_2:
    from urlparse import parse_qs, urljoin, urlparse
else:
    from urllib.parse import parse_qs, urljoin, urlparse

from robot.api import logger

from .keywords import Keywords
from .version import __version__


class REST(Keywords):
    """RESTinstance is revolutionary and peaceful HTTP JSON API test library.

    It guides you to write more stable API tests relying on constraints (e.g. "people's email addresses must be valid"), rather than on values having the nature of change (e.g "the first created user's email is expected to stay foo@bar.com").

    It bases on observations that we are more often concerned whether and which properties changed, when they should (not) had as this signals a bug, and less often what the actual values were/are. This also helps in tackling tests failing only because the test environment data was (not) reset.

    These resolutions in mind, it walks the path with you to contract-driven testing, from automatically generated JSON Schema data models to having formal OpenAPI service specs, as the both are essentially of the same origin. Both are also supported by major forces (Google, Microsoft, IBM et al. founded OpenAPI Initiative), and are language-agnostic which goes as well with Robot Framework.

    Contracts represent a common language within software teams, recognising our differing talents as designers, developers and test experts; or perhaps your new business companion wants to integrate to the system as well, but there is still some noise in signal - yet you don't feel very content providing them the source code, let alone explaining technical details, like which JSON properties are must in the response body, over the phone.

    Rest your mind. OSS got your back.


    = Tutorial =

    == Part 1: The API testing basics ==

    TODO to cover:
    - library init
        - url
        - ssl verify
        - content type
        - headers
    - inputs
        - strings in place (Python, JSON)
        - JSON files
        - variables (string, list, dict)
        - Python variable files
    - http keywords
        - timeouts
        - allow redirects
        - overriding headers
    - assertions
        - types (KW names) and enums (optional)
        - JSON Schema validation keywords
        - matching JSON properties
            - using clear text path
            - multiple matches using JSONPath
    - output
        - request, response
        - writing to file
        - the state (`Rest instances`)

    === Non-RESTful tests ===

    Sometimes you want to test workflows where multiple APIs must be called
    in some specific order, e.g. GETting a response body from one endpoint,
    then `POST`ing some of its properties as the new request body to some
    other endpoint:

    [example]


    == Part 2: Model based testing with JSON Schema ==

    The library generates JSON Schema for the request body and query params,
    and response body automatically, which can be output as following:

    [example]

    Notice that the generated schemas do not fix the property values,
    but the types, properties of the objects and items of the list.

    The generated schema gets more accurate by using assertion keywords
    in the test case level:

    [example]

    Notice that these advance the schema further.
    This applies as long as the assertions still still pass.

    The generated schemas are JSON themselves, thus can be output as JSON files,
    and then reused as expectations for further tests to avoid duplication:

    [example]

    This is useful if e.g. if you notice testing different HTTP methods,
    that essentially respond very similar JSON objects, with only minor
    differences in the presence or the absence of some properties in the JSON:

    [example]

    Commiting the automatically generated schemas to the git repository, and
    using the with expectation keywords (either in suite or test setups)
    before the requests happen (in test case level), works quite well
    for ensuring that the tests fail when the API breaks.

    However, this approach does not guarantee meaningful tests from API
    usage point of view: As only the JSON properties and their types are
    verified, this does not yet emphasize writing tests that actually have
    the ability to tell the reader, what are the meaningful properties
    in terms this particular request, or in the response gotten from
    that endpoint:

    [example]

    As of writing this, the machines have not yet gain the knowledge
    to infer what is meaningful to test. Hence, the library provides the
    assertion keywords to both improve the schemas further by your wisdom,
    and for the sake of readability, to clearly state the important properties
    on the test case level:

    [example]

    Similarly as using assertion keywords in the test cases, to emphasize the
    importantness of the particular JSON property, e.g. that sane error messages
    are responded by the API if the request body is missing something,
    the values can be explicitly, and visibly, asserted on the test case level
    to emphasize the importantness of immutability:

    [example]

    Notice how this test explicitly states to the reader,
    that the response status codes must stay as they are,
    as e.g. the clients do not know start retrying in case of timeouts.


    == Part 3: Towards contract-driven testing with OpenAPI ==

    Currently OpenAPI version 2.0 ("Swagger") is supported, but as 3.0.0 is
    gaining more popularity in Python schene as well, this might change soon.

    As JSON Schema is suitable for defining what kind of JSON data should,
    or should not be send or gotten from the API, but not enough for
    modeling the services as in defining what endpoints allow what
    properties to be changed, and what schema the request or response
    should follow, the library dives into further contract-driven testing
    by making possible to expect Swagger/OpenAPI specification:

    [example]

    This allows to expect the spec in the suite setup, and liberate us
    to only have to send the requests with (possibly even randomized)
    params on the test case level:

    [example]

    Notice how this leads to very clean looking tests.


    = On library design =

    The library also represents its own state as JSON itself.
    The state is a list of objects, "instances", each of which always
    having the three properties:

    - Request data as a object
    - Response data as a object
    - Schema for the request and the response as their respective objects

    The scope of the library is test suite, meaning, the instances are
    persisted in memory until the execution of the test suite is finished,
    either successfully or not (due to a fatal error or failing test).
    The instances, effectively the state, can be output to a JSON file using `RESTinstances` keyword. This output is mostly useful for machines though.

    By design, this library is intended to be used so that one test suite file
    is used per one API (the same path, the same resource) and containing
    all the methods with valid, invalid and missing requests in that suite.
    `Expect Spec` validates all of these requests and their responses against
    a Swagger 2.0 spec, which is commonly used in the suite setup.

    The core functionality of the library is, that for each request-response,
    as soon as the response has been gotten (and request did not timeout),
    a new "instance" is created. It has the properties described above,
    and is stored in the instances as the topmost item in the list.

    All the schemas, both generated and user inputted, are JSON Schema either
    draft-04 or draft-06 compliant. The draft version is defined in the schema.

    The schemas are generated automatically for request 'body' and 'query'
    and response 'body' JSON, unless the user has used expectation keywords
    to explicitly provide own schema for request or response, or both,
    in which is case the expected is preserved instead, and not overridden.

    This helps in testing the similarly responding methods. Do remember though,
    that the library works in the suite scope, so the expectations are persisted
    between test cases. This holds true, unless `Clear Expectations` is called, e.g. in test teardown, where this keyword is the most valuable in.

    All assertions are implemented by validating the JSON properties against
    the respective properties in the schema. These assertions first update the schema basing on what user is asserting, and then run the validations.
    The assertions do not require any any values or validations, only the type
    which is included in the keyword name.

    The assertion keywords correspond to the JSON types, and all of
    their validations, including the type, are implemented by JSON Schema.
    Some of the validations are common for all types and some are type specific.
    By design, the library assumes that at least the expected type is known.

    The property to assert is selected either using a plain text path,
    which is name of the keys in the JSON, going deeper and the keys
    separated by spaces. For JSON arrays, numbers can be used as indexes
    (starting from 0).

    A more powerful option for matching values to to use JSONPath as the query.
    Additionally, this allows matching multiple properties (or array items)
    in the JSON, and is quite useful in shortening otherwise very lengthy
    plain text paths, or e.g. validating that all the /users really have that
    email defined. but be careful of not mathing too much.

    The asserts check the property in this order:
    1. type matches the expected
    2. the value, or at least one them, given in enum, matches
    3. validations

    The assertion keywords are effective only for the last created instance, meaning that execution is stopped as soon as the first keyword fails,
    meaning the first error is occurred.

    There are three ways affecting whether tests pass or not.
    They are listed by the order of magnitude, and topmost overrides below :
    - Use `Expect Spec` in the suite setup and put all of that APIs requests
      to that particular test suite file. Remember the suite scope.
    - Use `Expect Response` or `Expect Request` for asserting that all the
      upcoming requests validates against this schema, before any further
      validations happen on the test case level (using Assertion keywords).
    - Use Assertion keywords for asserting one or many (JSONPath) properties

    The library provides `Output` keyword for writing the last instance
    as JSON to the terminal, or alternatively to a file created at the
    given path. By default, the output goes to terminal which is often
    more useful for debugging purposes.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    # Altogether 24 keywords        context:
    # -------------------------------------------------------
    # 2 setting keywords            next instances
    # 4 expectation keywords        next instances
    # 7 operation keywords          next instance
    # 8 assertion keywords          last instance's schema
    # 3 I/O keywords                the last instance or none
    # -------------------------------------------------------

    def __init__(self, url=None,
                 ssl_verify=True,
                 accept="application/json, */*",
                 content_type="application/json",
                 user_agent="RESTinstance/%s" % (__version__),
                 proxies={},
                 schema={},
                 spec={},
                 instances=[]):
        self.request = {
            'method': None,
            'url': None,
            'scheme': "",
            'netloc': "",
            'path': "",
            'query': {},
            'body': None,
            'headers': {
                'Accept': REST._input_string(accept),
                'Content-Type': REST._input_string(content_type),
                'User-Agent': REST._input_string(user_agent)
            },
            'proxies': REST._input_object(proxies),
            'timeout': [None, None],
            'cert': None,
            'sslVerify': REST._input_ssl_verify(ssl_verify),
            'allowRedirects': True
        }
        if url:
            url = REST._input_string(url)
            if url.endswith('/'):
                url = url[:-1]
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            url_parts = urlparse(url)
            self.request['scheme'] = url_parts.scheme
            self.request['netloc'] = url_parts.netloc
            self.request['path'] = url_parts.path
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
    def log_json(json, header="", also_console=True, sort_keys=False):
        json = dumps(json, ensure_ascii=False, indent=4,
                     separators=(',', ': ' ), sort_keys=sort_keys)
        logger.info("%s\n%s" % (header, json))    # no coloring for log.html
        if also_console:
            json_data = highlight(json,
                                  lexers.JsonLexer(),
                                  formatters.TerminalFormatter())
            logger.console("%s\n%s" % (header, json_data), newline=False)
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
        if isinstance(value, (float, int)):
            return value
        try:
            json_value = loads(value)
            if not isinstance(json_value, (float, int)):
                raise TypeError("This is not a Python float or integer: %s" % (
                    json_value))
        except (ValueError, TypeError):
            raise RuntimeError("This is not a JSON number:\n%s" % (value))
        return json_value

    @staticmethod
    def _input_string(value):
        if value == "":
            return ""
        if isinstance(value, STRING_TYPES):
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
            try:
                with open(path, encoding="utf-8") as file:
                    return load_yaml(file)
            except ValueError:
                raise RuntimeError("File '%s' is not valid JSON or YAML:\n%s" %
                    (path, e))

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
        if value is None or value == "null":
            return None
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
    def _input_ssl_verify(value):
        try:
            return REST._input_boolean(value)
        except RuntimeError:
            value = REST._input_string(value)
            if not path.isfile(value):
                raise RuntimeError("This SSL verify option is neither " +
                    "a Python or JSON boolean, nor a path to an existing " +
                    "CA bundle file:\n%s" % (value))
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
