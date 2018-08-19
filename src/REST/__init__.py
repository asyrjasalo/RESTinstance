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
    """Robot Framework test library for (RESTful) JSON APIs.


    RESTinstance guides you to write API tests to base on constraints,
    e.g. "people's emails must be a syntactically valid email addresses",
    rather than on specific values, which are often prone to change
    (e.g "the first created user's email is expected to stay as "foo@bar.com").

    It bases on the fact the we are more often interested whether the value
    changed when it should had, or should not had, as this might indicate a bug,
    and less often interested in what the value actually was, and now is.

    This approach also helps in tackling tests that fail regularly (only)
    because the test environment data was reset, but the values used in the
    tests weren't updated.



    == Towards contract-based API testing ==

    The library generates JSON Schema for the request and responses properties
    automatically, but does not fix the property values in the schema,
    unless this is explicitly wanted. The schema then gets more accurate by
    using assertion keywords in the test case level. Passing assertions
    advance the schema further, assuming the validations still pass.

    This schema can also be output, stored and reused as the base for testing
    the other methods, endpoints or params, but with minimum changes and without
    excessive duplication of the test data for otherwise very similarly
    responding methods.

    As JSON Schema is suitable for defining what kind of JSON data should,
    or should not be send or gotten from the API, but not that suitable
    in modeling the service - meaning, defining what endpoints allow what
    properties changed, and what schema the response should conform,
    the library dives into further contract-based testing by making possible
    to expect Swagger/OpenAPI specification on the suite setup level,
    and then liberate the tester to only have to send the requests with
    (possibly even randomized) params on the test case level.
    This leads to very clean looking tests.

    OpenAPI specs act well as a common language within the team,
    at same time recognizing our differing specilities as designers,
    developers, and testers. Or possibly you want to pressure the external parties
    to hurry up integrating to your system, but there is some noise in signal,
    and you do not feel very content providing them the source code,
    let alone telling which particular JSON fields are required in the response
    body, over the phone.

    Currently OpenAPI version 2.0 ("Swagger") is supported, but as 3.0.0 is
    gaining more popularity in Python scene too, this might change soon.



    == How to use the library efficiently ==

    The library also represents its own state as JSON itself.

    The state is a list of objects, "instances", each of which always
    having the three properties:

    - Request data as a object
    - Response data as a object
    - Schema for the request and the response as their respective objects

    The scope of the library is test suite, meaning, the instances are
    persisted in memory until the execution of the test suite is finished,
    either successfully or not (due to a fatal error or failing test).
    The instances, effectively the state, can be output to a JSON file using `RESTinstances` keyword. Beware, it might be mostly useful for machines though.

    By design, this library is intended to be used so that one test suite file
    is used per one API (the same path, the same resource) and containing
    all the methods with valid, invalid and missing requests in that suite.
    `Expect Spec` validates all of these requests and their responses against
    a Swagger 2.0 spec, which is commonly used in the suite setup.

    The core functionality of the library is, that for each request-response,
    as soon as the response has been gotten (and request did not timeout),
    a new "instance" is created. It has the properties described above,
    and is stored in the instances as the topmost item in the list.

    All the schemas, both generated, and user inputted, are JSON Schema draft-04
    compliant. The support for draft-06 is done, but not merged at this
    point, as it is more important to have the sensible documentation out.
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



    == Writing valuable but value-agnostic tests ==

    The generated schemas are JSON themselves, thus can be output as JSON files,
    and reused as expectations for further tests, or to avoid boilerplate.
    This is useful if e.g. if you notice testing different HTTP methods,
    that essentially respond very similar JSON objects, with only minor
    differences in the presence or the absence of some properties in the JSON.

    Commiting the automatically generated schemas to the git repository, and
    using the with expectation keywords (either in suite or test setups)
    before the requests happen (in test case level), works quite well
    for ensuring that the tests go red when the API breaks, or when it was
    monkeypatched with hair on fire, without the schemas being first updated.

    However, this quite automatic approach does not guarantee very
    meaningful tests from the actual API usage point of view:
    As only the constancy of the JSON properties and their types are then
    verified, this does not put enough weight to writing tests that actually
    have the ability to tell the reader, what are the meaningful properties
    in terms this particular request, or in the response gotten from
    that endpoint.

    Sometimes values make very much sense, e.g. in workflows where multiple
    APIs must be called in some specific order, e.g. GET a response body
    from one endpoint, then `POST`ing some of its properties as the new request body, to some another endpoint. This is not very RESTful indeed,
    but possible.

    Similarly as using assertion keywords in the test cases, to emphasize the
    importantness of the particular JSON property, e.g. that sane error messages
    are responded by the API if the request body is missing something,
    the values can be explicitly, and visibly, asserted on the test case level
    to emphasize the importantness of immutability, e.g. that the response status codes must be as they are, as the clients do not know start retrying
    in case of timeouts.

    As of writing this, the machines have not yet gain the knowledge
    to infer what is meaningful to test. Hence, the library provides the
    assertion keywords to both improve the schemas further by your wisdom,
    and for the sake of readability, to clearly state the important properties
    on the test case level.

    For now, it seems like our ability to think "outside the box",
    use a common language to express it, and leave some documentation for the
    upcoming generations probably gives us some advantages over the machines,
    in the software testing area at least.



    == Editors for OpenAPI specs? ==

    If you find hard it hard first to understanding OpenAPI specifications
    just by looking, reading and experimenting on them,
    you might have more luck with `Apicur <https://studio.apicur.io>`.

    It essentially looks one of the promising (free) web-based GUIs
    for creating and editing Swagger/OpenAPI specifications.



    The documentation is still prone to get more organized for 1.0.0.

    The library documentation was not written by a computer.
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
