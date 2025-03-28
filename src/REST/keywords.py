# RESTinstance (https://github.com/asyrjasalo/RESTinstance)
# Robot Framework library for RESTful JSON APIs.
#
# Copyright(C) 2018- Anssi Syrjäsalo (http://a.syrjasalo.com)
# Licensed under GNU Lesser General Public License v3 (LGPL-3.0).

import warnings
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from io import open
from json import dumps
from os import getcwd, path
from urllib.parse import parse_qsl, urljoin, urlparse

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from flex.core import validate_api_call

from genson import SchemaBuilder
from jsonpath_ng.ext import parse as parse_jsonpath
from jsonschema import FormatChecker, validate
from jsonschema.exceptions import SchemaError, ValidationError
from openapi_core import OpenAPI
from openapi_core.contrib.requests import (
    RequestsOpenAPIRequest,
    RequestsOpenAPIResponse,
)
from openapi_core.exceptions import OpenAPIError
from pytz import UnknownTimeZoneError, utc
from requests import request as client
from requests.auth import HTTPBasicAuth, HTTPDigestAuth, HTTPProxyAuth
from requests.exceptions import SSLError, Timeout
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from tzlocal import get_localzone

from .schema_keywords import SCHEMA_KEYWORDS


class Keywords:
    def get_keyword_names(self):
        return [
            name
            for name in dir(self)
            if hasattr(getattr(self, name), "robot_name")
        ]

    ### Keywords start here

    @keyword(name="Set Client Cert", tags=("settings",))
    def set_client_cert(self, cert):
        """*Sets the client cert for the requests.*

        The cert is either a path to a .pem file, or a JSON array, or a list, or a tuple
        having the cert path and the key path.

        Values ``null`` and ``${None}`` can be used for clearing the cert.

        *Examples*

        | `Set Client Cert` | ${CURDIR}/client.pem |
        | `Set Client Cert` | ["${CURDIR}/client.cert", "${CURDIR}/client.key"] |
        | `Set Client Cert` | ("${CURDIR}/client.cert", "${CURDIR}/client.key") |
        | `Set Client Cert` | ${paths_list} |
        """
        self.request["cert"] = self._input_client_cert(cert)
        return self.request["cert"]

    @keyword(name="Set Client Authentication", tags=("settings",))
    def set_client_authentication(self, auth_type, user=None, password=None):
        """*Attaches HTTP basic authentication to the given requests.*

        The API by default will not have authentication enabled.

        The auth_type argument must be ${NONE}, basic, digest or proxy.
        In case the user sets the auth_type to ${NONE} the authentication
        information
        The user and password will be written in plain text.

        *Examples*

        | `Set Client Authentication` | basic  | admin | password |
        | `Set Client Authentication` | digest | admin | password |
        | `Set Client Authentication` | proxy  | admin | password |
        | `Set Client Authentication` | ${NONE} | | |
        """
        error_auth = (
            'Argument "auth_type" must be ${NONE}, basic, digest or proxy.'
        )
        if auth_type is not None:
            if not isinstance(auth_type, str):
                raise TypeError(error_auth)

            auth_type = auth_type.lower()

            if auth_type not in ["basic", "digest", "proxy"]:
                raise TypeError(error_auth)

            if auth_type == "basic":
                auth_type = HTTPBasicAuth
            elif auth_type == "digest":
                auth_type = HTTPDigestAuth
            elif auth_type == "proxy":
                auth_type = HTTPProxyAuth

        return self._set_auth(auth_type, user, password)

    @keyword(name="Set Headers", tags=("settings",))
    def set_headers(self, headers):
        """*Sets new request headers or updates the existing.*

        ``headers``: The headers to add or update as a JSON object or a
        dictionary.

        *Examples*

        | `Set Headers` | { "authorization": "Basic QWxhZGRpbjpPcGVuU2VzYW1"} |
        | `Set Headers` | { "Accept-Encoding": "identity"} |
        | `Set Headers` | ${auth_dict} |
        """
        self.request["headers"].update(self._input_object(headers))
        return self.request["headers"]

    @keyword(name="Expect Request", tags=("expectations",))
    def expect_request(self, schema, merge=False):
        """*Sets the schema to validate the request properties*

        Expectations are effective for following requests in the test suite,
        or until they are reset or updated by using expectation keywords again.
        On the test suite level (suite setup), they are best used for expecting
        the endpoint wide properties that are common regardless of the tested
        HTTP method, and on the test case level (test setup) to merge in
        the HTTP method specific properties.

        `Expect Request` is intented to be used with tests that have some of the
        request properties, e.g. body or query parameters, randomized ("fuzzing")
        for validating that the sent values are within the expected scope.

        If the keyword is used, following HTTP keywords will fail when
        their request properties are not valid against the expected schema.

        If the keyword is not used, a new schema is generated for each following
        request for its ``body`` and ``query`` properties. Use `Output Schema` to output it and use it as an input to this keyword.

        *Options*

        ``merge``: Merges the new schema with the current instead of replacing it

        *Examples*

        | `Expect Request` | ${CURDIR}/valid_payload.json | | # See `Output Schema` |
        | `Expect Request` | { "body": { "required": ["id"] } } | merge=true |
        """
        schema = self._input_object(schema)
        if "properties" not in schema:
            schema = {"properties": schema}
        if self._input_boolean(merge):
            new_schema = SchemaBuilder(schema_uri=False)
            new_schema.add_schema(self.schema["properties"]["request"])
            new_schema.add_schema(schema)
            self.schema["properties"]["request"] = new_schema.to_schema()
        else:
            self.schema["properties"]["request"] = schema
        return self.schema["properties"]["request"]

    @keyword(name="Expect Response", tags=("expectations",))
    def expect_response(self, schema, merge=False):
        """*Sets the schema to validate the response properties.*

        Expectations are effective for following requests in the test suite,
        or until they are reset or updated by using expectation keywords again.
        On the test suite level (suite setup), they are best used for expecting
        the endpoint wide properties that are common regardless of the tested
        HTTP method, and on the test case level (test setup) to merge in
        the HTTP method specific properties.

        `Expect Response` is intented to be used on the suite level to validate
        the endpoint properties that hold regardless of the HTTP method,
        such as body property types, responded headers, authentication, etc.

        If the keyword is used, following HTTP keywords will fail when
        their response properties are not valid against the expected schema.

        If the keyword is not used, a new schema is inferred for each following
        response for its ``body``. Use `Output Schema` to output it and use it
        as an input to this keyword.

        *Options*

        ``merge``: Merges the new schema with the current instead of replacing it

        *Examples*

        | `Expect Response` | ${CURDIR}/endpoint_data_model.json | | # See `Output Schema` |
        | `Expect Response` | { "headers": { "required": ["Via"] } } | merge=true |
        | `Expect Response` | { "seconds": { "maximum": "1.0" } } | merge=true |
        """
        schema = self._input_object(schema)
        if "properties" not in schema:
            schema = {"properties": schema}
        if self._input_boolean(merge):
            new_schema = SchemaBuilder(schema_uri=False)
            new_schema.add_schema(self.schema["properties"]["response"])
            new_schema.add_schema(schema)
            self.schema["properties"]["response"] = new_schema.to_schema()
        else:
            self.schema["properties"]["response"] = schema
        return self.schema["properties"]["response"]

    @keyword(name="Expect Response Body", tags=("expectations",))
    def expect_response_body(self, schema):
        """*Updates the schema to validate the response body properties.*

        Expectations are effective for following requests in the test suite,
        or until they are reset or updated by using expectation keywords again.
        On the test suite level (suite setup), they are best used for expecting
        the endpoint wide properties that are common regardless of the tested
        HTTP method, and on the test case level (test setup) to merge in
        the HTTP method specific properties.

        `Expect Response Body` is intented to be used on the test case level,
        to validate that the response body has the expected properties for
        the particular HTTP method. Note that if something about response body
        has been already expected with `Expected Response`, using this keyword
        updates the expectations in terms of given response body properties.

        If the keyword is used, following HTTP keywords will fail if
        their response body is not valid against the expected schema.

        If the keyword is not used, and no schema is already expected with
        `Expect Response` for response ``body``, a new schema is inferred for it.
        Use `Output Schema` to output it and use it as an input to this keyword.

        *Tips*

        Regardless whether the HTTP method returns one (an object) or many
        (an array of objects), the validation of the object property types and features can usually be done to some extent on the test suite level
        with `Expect Response`, then extended on the test case level using this
        keyword. This helps in ensuring that the data model is unified between
        the different HTTP methods.

        *Examples*

        | `Expect Response Body` | ${CURDIR}/user_properties.json | # See `Output Schema` |
        | `Expect Response Body` | { "required": ["id", "token"] } | # Only these are required from this method |
        | `Expect Response Body` | { "additionalProperties": false } | # Nothing extra should be responded by this method |
        """
        response_properties = self.schema["properties"]["response"][
            "properties"
        ]
        if "body" in response_properties:
            response_properties["body"].update(self._input_object(schema))
        else:
            response_properties["body"] = self._input_object(schema)
        return response_properties["body"]

    @keyword(name="Clear Expectations", tags=("expectations",))
    def clear_expectations(self):
        """*Resets the expectations for both request and response.*

        Using this keyword resets any expectations set with keywords
        `Expect Response`, `Expect Response Body` and `Expect Request`.
        """
        self.schema["properties"]["request"] = {
            "type": "object",
            "properties": {},
        }
        self.schema["properties"]["response"] = {
            "type": "object",
            "properties": {},
        }
        return self.schema

    @keyword(name="HEAD", tags=("http",))
    def head(
        self,
        endpoint,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        loglevel=None,
    ):
        """*Sends a HEAD request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If true, follow all redirects.
        In contrary to other methods, no HEAD redirects are followed by default.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: The headers to add or override for this request.

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `HEAD` | /users/1 |
        | `HEAD` | /users/1 | timeout=0.5 |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "HEAD"
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="OPTIONS", tags=("http",))
    def options(
        self,
        endpoint,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        loglevel=None,
    ):
        """*Sends an OPTIONS request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: Headers as a JSON object to add or override for the request.

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `OPTIONS` | /users/1 |
        | `OPTIONS` | /users/1 | allow_redirects=false |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "OPTIONS"
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="GET", tags=("http",))
    def get(
        self,
        endpoint,
        query=None,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        data=None,
        loglevel=None,
    ):
        """*Sends a GET request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``query``: Request query parameters as a JSON object or a dictionary.
        Alternatively, query parameters can be given as part of endpoint as well.

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: Headers as a JSON object to add or override for the request.

        ``data``: Data as a dictionary, bytes or a file-like object

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `GET` | /users/1 |
        | `GET` | /users | timeout=2.5 |
        | `GET` | /users?_limit=2 |
        | `GET` | /users | _limit=2 |
        | `GET` | /users | { "_limit": "2" } |
        | `GET` | https://jsonplaceholder.typicode.com/users | headers={ "Authentication": "" } |

        *Data argument is new in version 1.1.0*
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "GET"
        request["query"] = OrderedDict()
        query_in_url = OrderedDict(parse_qsl(urlparse(endpoint).query))
        if query_in_url:
            request["query"].update(query_in_url)
            endpoint = endpoint.rsplit("?", 1)[0]
        if query:
            request["query"].update(self._input_object(query))
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        if data:
            request["data"] = self._input_data(data)
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="POST", tags=("http",))
    def post(
        self,
        endpoint,
        body=None,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        data=None,
        loglevel=None,
    ):
        """*Sends a POST request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``body``: Request body parameters as a JSON object, file or a dictionary.

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: Headers as a JSON object to add or override for the request.

        ``data``: Data as a dictionary, bytes or a file-like object

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `POST` | /users | { "id": 11, "name": "Gil Alexander" } |
        | `POST` | /users | ${CURDIR}/new_user.json |

        *Data argument is new in version 1.1.0*
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "POST"
        request["body"] = self.input(body)
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        if data:
            request["data"] = self._input_data(data)
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="PUT", tags=("http",))
    def put(
        self,
        endpoint,
        body=None,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        data=None,
        loglevel=None,
    ):
        """*Sends a PUT request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``body``: Request body parameters as a JSON object, file or a dictionary.

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: Headers as a JSON object to add or override for the request.

        ``data``: Data as a dictionary, bytes or a file-like object

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `PUT` | /users/2 | { "name": "Julie Langford", "username": "jlangfor" } |
        | `PUT` | /users/2 | ${dict} |

        *Data argument is new in version 1.1.0*
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "PUT"
        request["body"] = self.input(body)
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        if data:
            request["data"] = self._input_data(data)
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="PATCH", tags=("http",))
    def patch(
        self,
        endpoint,
        body=None,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        data=None,
        loglevel=None,
    ):
        """*Sends a PATCH request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``body``: Request body parameters as a JSON object, file or a dictionary.

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: Headers as a JSON object to add or override for the request.

        ``data``: Data as a dictionary, bytes or a file-like object

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `PATCH` | /users/4 | { "name": "Clementine Bauch" } |
        | `PATCH` | /users/4 | ${dict} |

        *Data argument is new in version 1.1.0*
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "PATCH"
        request["body"] = self.input(body)
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        if data:
            request["data"] = self._input_data(data)
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="DELETE", tags=("http",))
    def delete(
        self,
        endpoint,
        body=None,
        timeout=None,
        allow_redirects=None,
        validate=True,
        headers=None,
        loglevel=None,
    ):
        """*Sends a DELETE request to the endpoint.*

        The endpoint is joined with the URL given on library init (if any).
        If endpoint starts with ``http://`` or ``https://``, it is assumed
        an URL outside the tested API (which may affect logging).

        *Options*

        ``body``: Request body parameters as a JSON object, file or a dictionary.

        ``timeout``: A number of seconds to wait for the response before failing the keyword.

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set
        by expectation keywords and a spec given on library init.

        ``headers``: Headers as a JSON object to add or override for the request.

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*

        | `DELETE` | /users/6 |
        | `DELETE` | http://localhost:8273/state | validate=false |
        | `DELETE` | /users/6/pets | {"name" : "Rex","tagID" : "1234"} |

        *Body argument is new in version 1.1.0*
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request["method"] = "DELETE"
        request["body"] = self.input(body)
        if allow_redirects is not None:
            request["allowRedirects"] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request["timeout"] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request["headers"].update(self._input_object(headers))
        return self._request(endpoint, request, validate, loglevel)["response"]

    @keyword(name="Missing", tags=("assertions",))
    def missing(self, field):
        """*Asserts the field does not exist.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions],
        the root being the response body.

        *Examples*

        | `GET`     | /users/1 | # https://jsonplaceholder.typicode.com/users/1 |
        | `Missing` | response body password |
        | `Missing` | $.password |
        | `Missing` | $..geo.elevation | # response body address geo elevation |

        | `GET`     | /users | # https://jsonplaceholder.typicode.com/users |
        | `Missing` | response body 0 password |
        | `Missing` | $[*].password |
        | `Missing` | $[*]..geo.elevation |
        """
        try:
            matches = self._find_by_field(field, print_found=False)
        except AssertionError:
            return
        for found in matches:
            self.log_json(
                found["reality"],
                "\n\nExpected '%s' to not exist, but it is:" % (field),
            )
        raise AssertionError(
            "Expected '%s' to not exist, but it does." % (field)
        )

    @keyword(name="Null", tags=("assertions",))
    def null(self, field, **validations):
        """*Asserts the field as JSON null.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions],
        the root being the response body.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/generic.html|common for all types]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `PUT`  | /users/1 | { "deactivated_at": null } | # https://jsonplaceholder.typicode.com/users/1 |
        | `Null` | response body deactivated_at | |
        | `Null` | $.deactivated_at | | # JSONPath alternative |
        """
        values = []
        for found in self._find_by_field(field):
            reality = found["reality"]
            schema = {"type": "null"}
            skip = self._input_boolean(validations.pop("skip", False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name="Boolean", tags=("assertions",))
    def boolean(self, field, value=None, **validations):
        """*Asserts the field as JSON boolean.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions], the root being the response body.

        *Value*

        If given, the property value is validated in addition to the type.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/generic.html|common for all types]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `PUT`  | /users/1 | { "verified_email": true } | | | # https://jsonplaceholder.typicode.com/users/1 |
        | `Boolean` | response body verified_email | | | | # value is optional |
        | `Boolean` | response body verified_email | true |
        | `Boolean` | response body verified_email | ${True} | | | # same as above |
        | `Boolean` | $.verified_email | true | | | # JSONPath alternative |
        | `Boolean` | $.verified_email | true | enum=[1, "1"] | skip=true | # would pass |
        """
        values = []
        for found in self._find_by_field(field):
            reality = found["reality"]
            schema = {"type": "boolean"}
            if value is not None:
                schema["enum"] = [self._input_boolean(value)]
            elif self._should_add_examples():
                schema["examples"] = [reality]
            skip = self._input_boolean(validations.pop("skip", False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name="Integer", tags=("assertions",))
    def integer(self, field, *enum, **validations):
        """*Asserts the field as JSON integer.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions],
        the root being the response body.

        *Enum*

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/numeric.html#integer|for numeric types]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `GET`  | /users/1 | | # https://jsonplaceholder.typicode.com/users/1 |
        | `Integer` | response body id | | # value is optional |
        | `Integer` | response body id | 1 |
        | `Integer` | response body id | ${1} | # same as above |
        | `Integer` | $.id | 1 | # JSONPath alternative |

        | `GET`  | /users?_limit=10 | | | | # https://jsonplaceholder.typicode.com/users |
        | `Integer` | response body 0 id | 1 | | |
        | `Integer` | $[0].id | 1 | | | # same as above |
        | `Integer` | $[*].id | | minimum=1 | maximum=10 |
        """
        return self._assert_keyword("integer", field, *enum, **validations)

    @keyword(name="Number", tags=("assertions",))
    def number(self, field, *enum, **validations):
        """*Asserts the field as JSON number.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions],
        the root being the response body.

        *Enum*

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/numeric.html#number|for numeric types] can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `PUT`  | /users/1 | { "allocation": 95.0 } | # https://jsonplaceholder.typicode.com/users/1 |
        | `Number` | response body allocation | | # value is optional |
        | `Number` | response body allocation | 95.0 |
        | `Number` | response body allocation | ${95.0} | # same as above |
        | `Number` | $.allocation | 95.0 | # JSONPath alternative |

        | `GET`  | /users?_limit=10 | | | | # https://jsonplaceholder.typicode.com/users |
        | `Number` | $[0].id | 1 | | | # integers are also numbers |
        | `Number` | $[*].id | | minimum=1 | maximum=10 |
        """
        return self._assert_keyword("number", field, *enum, **validations)

    @keyword(name="String", tags=("assertions",))
    def string(self, field, *enum, **validations):
        """*Asserts the field as JSON string.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions], the root being the response body.

        *Enum*

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/string.html|for string]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `GET`  | /users/1 | | | # https://jsonplaceholder.typicode.com/users/1 |
        | `String` | response body email | | | # value is optional |
        | `String` | response body email | Sincere@april.biz |
        | `String` | $.email | Sincere@april.biz | | # JSONPath alternative |
        | `String` | $.email | | format=email |

        | `GET`  | /users?_limit=10 | | | # https://jsonplaceholder.typicode.com/users |
        | `String` | response body 0 email | Sincere@april.biz |
        | `String` | $[0].email | Sincere@april.biz | | # same as above |
        | `String` | $[*].email | | format=email |
        """
        return self._assert_keyword("string", field, *enum, **validations)

    @keyword(name="Object", tags=("assertions",))
    def object(self, field, *enum, **validations):
        """*Asserts the field as JSON object.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions], the root being the response body.

        *Enum*

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/object.html|for object]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `GET`  | /users/1 | | # https://jsonplaceholder.typicode.com/users/1 |
        | `Object` | response body | |
        | `Object` | response body | required=["id", "name"] | # can have other properties |

        | `GET`  | /users/1 | | # https://jsonplaceholder.typicode.com/users/1 |
        | `Object` | $.address.geo | required=["lat", "lng"] |
        | `Object` | $..geo | additionalProperties=false | # cannot have other properties |
        """
        return self._assert_keyword("object", field, *enum, **validations)

    @keyword(name="Array", tags=("assertions",))
    def array(self, field, *enum, **validations):
        """*Asserts the field as JSON array.*

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        [https://github.com/h2non/jsonpath-ng#jsonpath-syntax|supported JSONPath expressions],
        the root being the response body.

        *Enum*

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        *Validations*

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/array.html|for array]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*
        | `GET`  | /users?_limit=10 | | | | # https://jsonplaceholder.typicode.com/users |
        | `Array` | response body | | |
        | `Array` | $ | | | | # same as above |
        | `Array` | $ | minItems=1 | maxItems=10 | uniqueItems=true |
        """
        return self._assert_keyword("array", field, *enum, **validations)

    @keyword(name="Input", tags=("I/O",))
    def input(self, what):
        """*Converts the input to JSON and returns it.*

        Any of the following is accepted:

        - The path to JSON file
        - Any scalar that can be interpreted as JSON
        - A dictionary or a list

        *Examples*

        | ${payload} | `Input` | ${CURDIR}/payload.json |

        | ${object} | `Input` | { "name": "Julie Langford", "username": "jlangfor" } |
        | ${object} | `Input` | ${dict} |

        | ${array} | `Input` | ["name", "username"] |
        | ${array} | `Input` | ${list} |

        | ${boolean} | `Input` | true |
        | ${boolean} | `Input` | ${True} |

        | ${number} | `Input` | 2.0 |
        | ${number} | `Input` | ${2.0} |

        | ${string} | `Input` | Quotes are optional for strings |
        """
        if what is None:
            return None
        if not isinstance(what, str):
            return self._input_json_from_non_string(what)
        if path.isfile(what):
            return self._input_json_from_file(what)
        try:
            return self._input_json_as_string(what)
        except ValueError:
            return self._input_string(what)

    @keyword(name="Output Schema", tags=("I/O",))
    def output_schema(
        self,
        what="",
        file_path=None,
        append=False,
        sort_keys=False,
        also_console=True,
    ):
        """*Outputs JSON Schema to terminal or a file.*

        By default, the schema is output for the last request and response.

        The output can be limited further by:

        - The property of the last instance, e.g. ``request`` or ``response``
        - Any nested property that exists, similarly as for assertion keywords

        Also variables and values that can be converted to JSON are accepted,
        in which case the schema is generated for those instead.

        *Options*

        ``file_path``: The JSON Schema is written to a file instead of terminal.
        The file is created if it does not exist.

        ``append``: If true, the JSON Schema is appended to the given file
        instead of truncating it first.

        ``sort_keys``: If true, the JSON Schema is sorted alphabetically by
        property names before it is output.

        ``also_console``: If false, the JSON Schema is not written to terminal. Default is true.

        *Examples*

        | `Output Schema` | response | ${CURDIR}/response_schema.json | # Write a file to use with `Expect Response` |
        | `Output Schema` | response body | ${CURDIR}/response_body_schema.json | # Write a file to use with `Expect Response Body` |

        | `Output Schema` | $.email | # only the schema for one response body property |
        | `Output Schema` | $..geo | # only the schema for the nested response body property |
        """
        if isinstance(what, (str)):
            if what == "":
                try:
                    json = self._last_instance_or_error()["schema"]
                except IndexError:
                    raise RuntimeError("No instances.")
            elif what.startswith(("request", "response", "$")):
                self._last_instance_or_error()
                matches = self._find_by_field(what)
                if len(matches) > 1:
                    json = [found["schema"] for found in matches]
                else:
                    json = matches[0]["schema"]
            else:
                try:
                    json = self._new_schema(self._input_json_as_string(what))
                except ValueError:
                    json = self._new_schema(self._input_string(what))
        else:
            json = self._new_schema(self._input_json_from_non_string(what))
        sort_keys = self._input_boolean(sort_keys)

        if isinstance(also_console, (str)):
            also_console = also_console.lower() == "true"
        self.log_json(json, sort_keys=sort_keys, also_console=also_console)

        if file_path:
            content = dumps(
                json,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": "),
                sort_keys=sort_keys,
            )
            write_mode = "a" if self._input_boolean(append) else "w"
            try:
                with open(
                    path.join(getcwd(), file_path), write_mode, encoding="utf-8"
                ) as file:
                    file.write(content)
            except OSError as e:
                raise RuntimeError(
                    f"Error outputting to file '{file_path}':\n{e}"
                )
        return json

    @keyword(name="Output", tags=("I/O",))
    def output(
        self,
        what="",
        file_path=None,
        append=False,
        sort_keys=False,
        also_console=True,
    ):
        """*Outputs JSON to terminal or a file.*

        By default, the last request and response are output to terminal.

        The output can be limited further by:

        - The property of the last instance, e.g. ``request`` or ``response``
        - Any nested property that exists, similarly as for assertion keywords

        Also variables and values that can be converted to JSON are accepted,
        in which case those are output as JSON instead.

        *Options*

        ``file_path``: The JSON is written to a file instead of terminal.
        The file is created if it does not exist.

        ``append``: If true, the JSON is appended to the given file
        instead of truncating it first.

        ``sort_keys``: If true, the JSON is sorted alphabetically by
        property names before it is output.

        ``also_console``: If false, the JSON is not written to terminal. Default is true.

        *Examples*

        | `Output` | response | # only the response is output |
        | `Output` | response body | # only the response body is output |
        | `Output` | $.email | # only the response body property is output |
        | `Output` | $..geo | # only the nested response body property is output |

        | `Output` | request | # only the request is output |
        | `Output` | request headers | # only the request headers are output |
        | `Output` | request headers Authentication | # only this header is output |

        | `Output` | response body | ${CURDIR}/response_body.json | | # write the response body to a file |
        | `Output` | response seconds | ${CURDIR}/response_delays.log | append=true | # keep track of response delays in a file |
        """
        if isinstance(what, (str)):
            if what == "":
                try:
                    json = deepcopy(self._last_instance_or_error())
                    json.pop("schema")
                    json.pop("spec")
                except IndexError:
                    raise RuntimeError("No instances.")
            elif what.startswith("schema"):
                logger.warn(
                    "Using `Output` for schema is deprecated. "
                    + "Using `Output Schema` to handle schema paths better."
                )
                what = what.lstrip("schema").lstrip()
                return self.output_schema(what, file_path, append, sort_keys)
            elif what.startswith(("request", "response", "$")):
                self._last_instance_or_error()
                matches = self._find_by_field(what, return_schema=False)
                if len(matches) > 1:
                    json = [found["reality"] for found in matches]
                else:
                    json = matches[0]["reality"]
            else:
                try:
                    json = self._input_json_as_string(what)
                except ValueError:
                    json = self._input_string(what)
        else:
            json = self._input_json_from_non_string(what)
        sort_keys = self._input_boolean(sort_keys)

        if isinstance(also_console, (str)):
            also_console = also_console.lower() == "true"
        self.log_json(json, sort_keys=sort_keys, also_console=also_console)
        if file_path:
            content = dumps(
                json,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": "),
                sort_keys=sort_keys,
            )
            write_mode = "a" if self._input_boolean(append) else "w"
            try:
                with open(
                    path.join(getcwd(), file_path), write_mode, encoding="utf-8"
                ) as file:
                    file.write(content)
            except OSError as e:
                raise RuntimeError(
                    f"Error outputting to file '{file_path}':\n{e}"
                )
        return json

    @keyword(name="REST Instances", tags=("I/O",))
    def rest_instances(self, file_path=None, sort_keys=False):
        """*Writes the instances as JSON to a file.*

        The instances are written to file as a JSON array of JSON objects,
        each object representing a single instance, and having three properties:

        - the request
        - the response
        - the schema for both, which have been updated according to the tests

        The file is created if it does not exist, otherwise it is truncated.

        *Options*

        ``sort_keys``: If true, the instances are sorted alphabetically by
        property names.

        *Examples*

        | `Rest Instances` | ${CURDIR}/log.json |
        """
        if not file_path:
            outputdir_path = BuiltIn().get_variable_value("${OUTPUTDIR}")
            if self.request["netloc"]:
                file_path = (
                    path.join(outputdir_path, self.request["netloc"]) + ".json"
                )
            else:
                file_path = path.join(outputdir_path, "instances") + ".json"
        sort_keys = self._input_boolean(sort_keys)
        content = dumps(
            self.instances,
            ensure_ascii=False,
            indent=4,
            default=vars,
            separators=(",", ": "),
            sort_keys=sort_keys,
        )
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
        except OSError as e:
            raise RuntimeError(
                "Error exporting instances " + f"to file '{file_path}':\n{e}"
            )
        return self.instances

    @keyword(name="Set SSL Verify", tags=("settings",))
    def set_ssl_verify(self, ssl_verify=True):
        """*Sets new SSL verify option*

        ``ssl_verify``: True/False or a location to a certificate file

        *Examples*

        | `Set SSL Verify` |  |
        | `Set SSL Verify` | False |
        | `Set SSL Verify` | cert.pem |
        """
        self.request["sslVerify"] = self._input_ssl_verify(ssl_verify)
        return self.request["sslVerify"]

    @keyword(name="Set Log Level", tags=("settings",))
    def set_log_level(self, loglevel):
        """*Sets the library log level to se specific value*

        ``loglevel``: INFO, DEBUG, TRACE, WARN, ERROR, HTML. Other values are
        automatically converted to WARN (library default).

        *Examples*
        | `Set Log Level` | DEBUG | |
        | `Set Log Level` | debug | # Same as above |
        | `Set Log Level` | NOTHING | # Will be converted to WARN|
        """
        self.log_level = self._input_log_level(loglevel)
        return self.log_level

    ### Internal methods

    def _set_auth(self, auth_type, user=None, password=None):
        if auth_type is None:
            self.auth = None
        else:
            self.auth = auth_type(user, password)
        return self.auth

    def _request(self, endpoint, request, validate=True, log_level=None):
        if not endpoint.startswith(("http://", "https://")):
            base_url = self.request["scheme"] + "://" + self.request["netloc"]
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
            endpoint = urljoin(base_url, self.request["path"]) + endpoint
        request["url"] = endpoint
        url_parts = urlparse(request["url"])
        request["scheme"] = url_parts.scheme
        request["netloc"] = url_parts.netloc
        request["path"] = url_parts.path
        request["auth"] = self.auth
        try:
            response = client(
                request["method"],
                request["url"],
                params=request["query"],
                json=request["body"],
                data=request["data"],
                headers=request["headers"],
                proxies=request["proxies"],
                cert=request["cert"],
                auth=request["auth"],
                timeout=tuple(request["timeout"]),
                allow_redirects=request["allowRedirects"],
                verify=request["sslVerify"],
            )
        except SSLError as e:
            raise AssertionError(
                "%s to %s SSL certificate verify failed:\n%s"
                % (request["method"], request["url"], e)
            )
        except Timeout as e:
            raise AssertionError(
                "%s to %s timed out:\n%s"
                % (request["method"], request["url"], e)
            )
        utc_datetime = datetime.now(tz=utc)
        request["timestamp"] = {}
        request["timestamp"]["utc"] = utc_datetime.isoformat()
        try:
            request["timestamp"]["local"] = utc_datetime.astimezone(
                get_localzone()
            ).isoformat()
        except UnknownTimeZoneError as e:
            logger.info("Cannot infer local timestamp! tzlocal:%s" % str(e))
        if validate and self.spec:
            self._assert_spec(self.spec, response)
        instance = self._instantiate(request, response, validate, log_level)
        self.instances.append(instance)
        return instance

    def _instantiate(
        self, request, response, validate_schema=True, log_level=None
    ):
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text
            if response_body:
                if not log_level:
                    log_level = self.log_level
                try:
                    headers = response.headers["Content-Type"]
                except KeyError:
                    headers = 'NO "Content-Type" HEADER FOUND'
                logger.write(
                    "Response body content is not JSON. "
                    + "Content-Type is: %s" % headers,
                    log_level,
                )
        response = {
            "seconds": response.elapsed.microseconds / 1000 / 1000,
            "status": response.status_code,
            "reason": response.reason,
            "body": response_body,
            "headers": dict(response.headers),
        }
        schema = deepcopy(self.schema)
        schema["title"] = "{} {}".format(request["method"], request["url"])
        try:
            schema["description"] = "{}: {}".format(
                BuiltIn().get_variable_value("${SUITE NAME}"),
                BuiltIn().get_variable_value("${TEST NAME}"),
            )
        except RobotNotRunningError:
            schema["description"] = ""
        request_properties = schema["properties"]["request"]["properties"]
        response_properties = schema["properties"]["response"]["properties"]
        if validate_schema:
            if request_properties:
                self._validate_schema(request_properties, request)
            if response_properties:
                self._validate_schema(response_properties, response)
        request_properties["body"] = self._new_schema(request["body"])
        request_properties["query"] = self._new_schema(request["query"])
        response_properties["body"] = self._new_schema(response["body"])
        if "default" in schema and schema["default"]:
            self._add_defaults_to_schema(schema, response)
        return {
            "request": request,
            "response": response,
            "schema": schema,
            "spec": self.spec,
        }

    def _assert_spec(self, spec, response):
        request = response.request

        spec_version = spec.get("openapi", "0")
        if spec_version.startswith("3"):
            try:
                if self._spec is None:
                    self._spec = OpenAPI.from_dict(self.spec)

                openapi_request = RequestsOpenAPIRequest(request)
                openapi_response = RequestsOpenAPIResponse(response)

                self._spec.validate_request(openapi_request)
                self._spec.validate_response(openapi_request, openapi_response)

            except OpenAPIError as e:
                raise AssertionError(e) from e
        else:
            try:
                validate_api_call(
                    spec, raw_request=request, raw_response=response
                )
            except ValueError as e:
                raise AssertionError(e)

    def _validate_schema(self, schema, json_dict):
        for field in schema:
            self._assert_schema(schema[field], json_dict[field])

    def _assert_schema(self, schema, reality):
        try:
            validate(reality, schema, format_checker=FormatChecker())
        except SchemaError as e:
            raise RuntimeError(e)
        except ValidationError as e:
            raise AssertionError(e)

    def _new_schema(self, value):
        builder = SchemaBuilder(schema_uri=False)
        builder.add_object(value)
        return builder.to_schema()

    def _add_defaults_to_schema(self, schema, response):
        body = response["body"]
        schema = schema["properties"]["response"]["properties"]["body"]
        if isinstance(body, (dict)) and "properties" in schema:
            self._add_property_defaults(body, schema["properties"])

    def _add_property_defaults(self, body, schema):
        for key in body:
            if "properties" in schema[key]:
                self._add_property_defaults(
                    body[key], schema[key]["properties"]
                )
            else:
                schema[key]["default"] = body[key]

    def _find_by_field(self, field, return_schema=True, print_found=True):
        last_instance = self._last_instance_or_error()
        schema = None
        paths = []
        if field.startswith("$"):
            value = last_instance["response"]["body"]
            if return_schema:
                schema = last_instance["schema"]["properties"]["response"]
                schema = schema["properties"]["body"]
            if field == "$":
                return [
                    {
                        "path": ["response", "body"],
                        "reality": value,
                        "schema": schema,
                    }
                ]
            try:
                query = parse_jsonpath(field)
            except Exception as e:
                raise RuntimeError(f"Invalid JSONPath query '{field}': {e}")
            matches = [str(match.full_path) for match in query.find(value)]
            if not matches:
                raise AssertionError(
                    "JSONPath query '%s' " % (field) + "did not match anything."
                )
            for match in matches:
                path = match.replace("[", "").replace("]", "").split(".")
                paths.append(path)
        else:
            value = last_instance
            if return_schema:
                schema = last_instance["schema"]["properties"]
            path = field.split()
            paths.append(path)
        return [
            self._find_by_path(field, path, value, schema, print_found)
            for path in paths
        ]

    def _last_instance_or_error(self):
        try:
            return self.instances[-1]
        except IndexError:
            raise RuntimeError(
                "No instances: No requests made, "
                + "and no previous instances loaded in the library import."
            )

    def _find_by_path(self, field, path, value, schema=None, print_found=True):
        for key in path:
            try:
                value = self._value_by_key(value, key)
            except (KeyError, TypeError):
                if print_found:
                    self.log_json(
                        value, "\n\nProperty '%s' does not exist in:" % (key)
                    )
                raise AssertionError(
                    "\nExpected property '%s' was not found." % (field)
                )
            except IndexError:
                if print_found:
                    self.log_json(
                        value, "\n\nIndex '%s' does not exist in:" % (key)
                    )
                raise AssertionError(
                    "\nExpected index '%s' did not exist." % (field)
                )
            if schema:
                schema = self._schema_by_key(schema, key, value)
        found = {"path": path, "reality": value, "schema": schema}
        return found

    def _value_by_key(self, json, key):
        try:
            return json[int(key)]
        except (ValueError, KeyError):
            return json[key]

    def _schema_by_key(self, schema, key, value):
        if "properties" in schema:
            schema = schema["properties"]
        elif "items" in schema:
            if isinstance(schema["items"], (dict)):
                schema["items"] = [schema["items"]]
            new_schema = self._new_schema(value)
            try:
                return schema["items"][schema["items"].index(new_schema)]
            except ValueError:
                schema["items"].append(new_schema)
                return schema["items"][-1]
        if key not in schema:
            schema[key] = self._new_schema(value)
        return schema[key]

    def _should_add_examples(self):
        return "examples" in self.schema and isinstance(
            self.schema["examples"], (list)
        )

    def _set_type_validations(self, json_type, schema, validations):
        if validations:
            if "draft-04" in self.schema["$schema"]:
                schema_version = "draft-04"
            elif "draft-06" in self.schema["$schema"]:
                schema_version = "draft-06"
            else:
                schema_version = "draft-07"
            kws = list(SCHEMA_KEYWORDS["common"][schema_version])
            kws.extend(SCHEMA_KEYWORDS[json_type][schema_version])
        for validation in validations:
            if validation not in kws:
                raise RuntimeError(
                    "Unknown JSON Schema (%s)" % (schema_version)
                    + " validation keyword "
                    + f"for {json_type}:\n{validation}"
                )
            schema[validation] = self.input(validations[validation])
        schema.update({"type": json_type})

    def _assert_keyword(self, input_type, field, *enum, **validations):
        input_methods = {
            "string": self._input_string,
            "integer": self._input_integer,
            "number": self._input_number,
            "array": self._input_array,
            "object": self._input_object,
        }
        values = []
        for found in self._find_by_field(field):
            schema = found["schema"]
            reality = found["reality"]
            skip = self._input_boolean(validations.pop("skip", False))
            self._set_type_validations(input_type, schema, validations)
            if enum:
                if "enum" not in schema:
                    schema["enum"] = []
                for value in enum:
                    value = input_methods[input_type](value)
                    if value not in schema["enum"]:
                        schema["enum"].append(value)
            elif self._should_add_examples():
                schema["examples"] = [reality]
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values
