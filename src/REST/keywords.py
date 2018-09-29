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

from pytz import utc
from tzlocal import get_localzone

from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from json import dumps, loads
from os import path, getcwd

from flex.core import validate_api_call
from genson import SchemaBuilder
from jsonpath_ng.ext import parse as parse_jsonpath
from jsonschema import Draft4Validator, Draft6Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from requests import request as client
from requests.exceptions import SSLError, Timeout

if IS_PYTHON_2:
    from urlparse import parse_qsl, urljoin, urlparse
else:
    from urllib.parse import parse_qsl, urljoin, urlparse

from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

from .schema_keywords import SCHEMA_KEYWORDS


class Keywords(object):

    def get_keyword_names(self):
        return [name for name in dir(self) if hasattr(getattr(self, name),
            'robot_name')]

    ### Keywords start here

    @keyword(name=None, tags=("settings",))
    def set_client_cert(self, cert):
        """
        Sets a client certificate for all the upcoming requests in test suite,
        for e.g. authentication. Overrides the previous if it was already set.

        Arguments:

        ``cert``:   Either a path to an SSL certificate `.pem` file,
                    or a (JSON) array containing `cert` and `key`,
                    or a (Python) list or tuple containing `cert` and `key`.
                    Respectively, values `"null"` and `${None}`
                    can be used to clear the setting.

        Returns:

            The current SSL certificate in use either as a Python string,
            list or a tuple, depending on what was originally given.
        """
        self.request['cert'] = self._input_client_cert(cert)
        return self.request['cert']

    @keyword(name=None, tags=("settings",))
    def set_headers(self, headers):
        """
        You can `Set Headers` one header at a time.

        Example:
        Set the authorization header and content type.
        | `Set Headers`     | {"authorization": "Basic Og=="}       |
        | `Set Headers`     | {"content-type": "application/json"}  |
        """
        self.request['headers'].update(self._input_object(headers))
        return self.request['headers']

    @keyword(name=None, tags=("expectations",))
    def expect_request(self, schema, replace=False):
        request_schema = self.schema['properties']['request']
        if self._input_boolean(replace):
            request_schema = self._input_object(schema)
        else:
            request_schema.update(self._input_object(schema))
        return request_schema

    @keyword(name=None, tags=("expectations",))
    def expect_response(self, schema, replace=False):
        response_schema = self.schema['properties']['response']
        if self._input_boolean(replace):
            response_schema = self._input_object(schema)
        else:
            response_schema.update(self._input_object(schema))
        return response_schema

    @keyword(name=None, tags=("expectations",))
    def expect_spec(self, spec, replace=False):
        if self._input_boolean(replace):
            self.spec = self._input_object(spec)
        else:
            self.spec.update(self._input_object(spec))
        return self.spec

    @keyword(name=None, tags=("expectations",))
    def clear_expectations(self):
        """Reset the schema for ``request`` and ``response`` back to empty or {}"""
        self.schema['properties']['request'] = {
            "type": "object",
            "properties": {}
        }
        self.schema['properties']['response'] = {
            "type": "object",
            "properties": {}
        }
        return self.schema

    @keyword(name=None, tags=("http",))
    def head(self, endpoint, timeout=None, allow_redirects=None, validate=True,
             headers=None):
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "HEAD"
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("http",))
    def options(self, endpoint, timeout=None, allow_redirects=None,
                validate=True, headers=None):
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "OPTIONS"
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("http",))
    def get(self, endpoint, query=None, timeout=None, allow_redirects=None,
            validate=True, headers=None):
        """Make a ``GET`` request call to a specified ``endpoint``.

        Example:
        GET users from site and ensure status code is 200
        | `GET`     | /users?limit=2  |     |
        | `Integer` | response status | 200 |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "GET"
        request['query'] = OrderedDict()
        query_in_url = OrderedDict(parse_qsl(urlparse(endpoint).query))
        if query_in_url:
            request['query'].update(query_in_url)
            endpoint = endpoint.rsplit('?', 1)[0]
        if query:
            request['query'].update(self._input_object(query))
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("http",))
    def post(self, endpoint, body=None, timeout=None, allow_redirects=None,
             validate=True, headers=None):
        """Make a ``POST`` request call to a specified ``endpoint``.

        Example:
        POST "Mr Potato" to endpoint and ensure status code is 201
        | `POST`    | /users          | { "id": 11, "name": "Mr Potato" } |
        | `Integer` | response status | 201                               |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "POST"
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("http",))
    def put(self, endpoint, body=None, timeout=None, allow_redirects=None,
            validate=True, headers=None):
        """Make a ``PUT`` request call to a specified ``endpoint``.

        Example:
        PUT existing record with new name to endpoint
        | `PUT`  | /users/11  | { "name": "Albus Potter" }  |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "PUT"
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("http",))
    def patch(self, endpoint, body=None, timeout=None, allow_redirects=None,
              validate=True, headers=None):
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "PATCH"
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("http",))
    def delete(self, endpoint, timeout=None, allow_redirects=None,
               validate=True, headers=None):
        """Make a ``DELETE`` request call to a specified ``endpoint``.

        Example:
        DELETE user 4 from endpoint and ensure status code is 200, 202, or 204.
        | `DELETE`  | /users/4        |     |     |     |
        | `Integer` | response status | 200 | 202 | 204 |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "DELETE"
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("assertions",))
    def missing(self, field):
        """Verify a specific ``field`` does not exist.

        Example:
        After I make a `GET` call, I want to verify the field is not in the response body.
        If ``shouldNotExist`` is in the body, then fail the assertion. If it is NOT in the body, then pass.
        | `GET`     | /users/4                     |
        | `Missing` | response body shouldNotExist |
        """
        try:
            matches = self._find_by_field(field, print_found=False)
        except AssertionError:
            return
        for found in matches:
            self.log_json(found['reality'],
                "\n\nExpected '%s' to not exist, but it is:" % (field))
        raise AssertionError("Expected '%s' to not exist, but it does." % (
            field))

    @keyword(name=None, tags=("assertions",))
    def null(self, field, **validations):
        """Verify a specific ``field`` is null.

        Example:
        After I make a `GET` call, I want to verify the field is null.
        If response body estate is null, then it is a success.
        | `GET`  | /users/4             |
        | `Null` | response body estate |
        """
        values = []
        for found in self._find_by_field(field):
            reality = found['reality']
            schema = { "type": "null" }
            skip = self._input_boolean(validations.pop('skip', False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("assertions",))
    def boolean(self, field, value=None, **validations):
        """Verify a specific ``field`` is a boolean with a specific value.

        Example:
        After I make a `GET` call, I want to verify the field is a boolean and is true.
        | `GET`     | /users/4                |      |
        | `Boolean` | response body isBananas | true |
        """
        values = []
        for found in self._find_by_field(field):
            reality = found['reality']
            schema = { "type": "boolean" }
            if value is not None:
                schema['enum'] = [self._input_boolean(value)]
            skip = self._input_boolean(validations.pop('skip', False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("assertions",))
    def integer(self, field, *enum, **validations):
        """Verify a specific ``field`` is an Integer with a specific value, or set of values.

        Example:
        After I make a `GET` call, I want to verify the field is an integer and has one or more of my integer values.
        If the response status returns a 200, 202, or 204, then it is a success.
        | `GET`     | /users/4        |     |     |     |
        | `Integer` | response status | 200 | 202 | 204 |
        """
        values = []
        for found in self._find_by_field(field):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("integer", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_integer(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("assertions",))
    def number(self, field, *enum, **validations):
        """Verify a specific ``field`` is a number(integer or floating) value, or set of values.

        Example:
        After I make a `GET` call, I want to verify the field is a number and has one or more of my number values.
        If the response body dollars returns a 42, 34.50, or 100, then it is a success.
        | `GET`     | /users/4              |    |       |     |
        | `Number` | response body dollars | 42 | 34.50 | 100 |
        """
        values = []
        for found in self._find_by_field(field):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("number", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_number(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("assertions",))
    def string(self, field, *enum, **validations):
        """Verify a specific ``field`` is a string with a specific value, or set of values.

        Example:
        After I make a `GET` call, I want to verify the field is a string and has one or more of my string values.
        If the response body name returns "Adam West" or "Peter Parker", then it is a success.
        | `GET`     | /users/4           |           |              |
        | `String`  | response body name | Adam West | Peter Parker |
        """
        values = []
        for found in self._find_by_field(field):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("string", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_string(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("assertions",))
    def object(self, field, *enum, **validations):
        """Verify a specific ``field`` is an object with a specific value, or set of values.

        Example:
        After I make a `GET` call, I want to verify the field is a object and has one or more of my values.
        If the response body animals returns an object, then it is a success.
        | `GET`     | /zoo/4                |
        | `Object`  | response body animals |
        """
        values = []
        for found in self._find_by_field(field):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("object", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_object(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("assertions",))
    def array(self, field, *enum, **validations):
        """Verify a returned response is an array with specific validations.

        Example:
        Verify the returned response is an array and has a maximum of 100 items.
        If more than 100 items, fail.
        | `GET`   | /users?limit=100 |                |
        | `Array` | response body    | maxItems = 100 |
        """
        values = []
        for found in self._find_by_field(field):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("array", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_array(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("I/O",))
    def input(self, what):
        if what is None:
            return None
        if not isinstance(what, STRING_TYPES):
            return self._input_json_from_non_string(what)
        if path.isfile(what):
            return self._input_json_from_file(what)
        try:
            return self._input_json_as_string(what)
        except ValueError:
            return self._input_string(what)

    @keyword(name=None, tags=("I/O",))
    def output_schema(self, what="", file_path=None, append=False,
                      sort_keys=False):
        message = "\n%s as JSON is:" % (what.__class__.__name__)
        if what == "":
            message = "\n\nThe current instance's JSON Schema is:"
            try:
                json = deepcopy(self._last_instance_or_error()['schema'])
                del json['$schema']
                del json['exampled']
            except IndexError:
                raise RuntimeError(no_instances_error)
        elif isinstance(what, (STRING_TYPES)):
            try:
                json = self._new_schema(loads(what))
            except ValueError:
                self._last_instance_or_error()
                message = "\n\n%s JSON Schema is:" % (what)
                matches = self._find_by_field(what)
                if len(matches) > 1:
                    json = [found['schema'] for found in matches]
                else:
                    json = matches[0]['schema']
        else:
            json = self._new_schema(what)
        sort_keys = self._input_boolean(sort_keys)
        if not file_path:
            self.log_json(json, message, sort_keys=sort_keys)
        else:
            content = dumps(json, ensure_ascii=False, indent=4,
                            separators=(',', ': ' ), sort_keys=sort_keys)
            write_mode = 'a' if self._input_boolean(append) else 'w'
            try:
                with open(path.join(getcwd(), file_path), write_mode,
                          encoding="utf-8") as file:
                    if IS_PYTHON_2:
                        content = unicode(content)
                    file.write(content)
            except IOError as e:
                raise RuntimeError("Error outputting to file '%s':\n%s" % (
                    file_path, e))
        return json


    @keyword(name=None, tags=("I/O",))
    def output(self, what="", file_path=None, append=False, sort_keys=False):
        """After a REST call, you can output the response.

        Example:
        `GET` users and `Output` the response body.
        | `GET`    | /users?limit=2  |
        | `Output` | response body   |

        """
        message = "\n%s as JSON is:" % (what.__class__.__name__)
        if what == "":
            message = "\n\nThe current instance as JSON is:"
            try:
                json = deepcopy(self._last_instance_or_error())
                del json['schema']
                del json['spec']
            except IndexError:
                raise RuntimeError(no_instances_error)
        elif isinstance(what, (STRING_TYPES)):
            try:
                json = loads(what)
            except ValueError:
                self._last_instance_or_error()
                message = "\n\n%s as JSON is:" % (what)
                matches = self._find_by_field(what, return_schema=False)
                if len(matches) > 1:
                    json = [found['reality'] for found in matches]
                else:
                    json = matches[0]['reality']
        else:
            json = what
        sort_keys = self._input_boolean(sort_keys)
        if not file_path:
            self.log_json(json, message, sort_keys=sort_keys)
        else:
            content = dumps(json, ensure_ascii=False, indent=4,
                            separators=(',', ': ' ), sort_keys=sort_keys)
            write_mode = 'a' if self._input_boolean(append) else 'w'
            try:
                with open(path.join(getcwd(), file_path), write_mode,
                          encoding="utf-8") as file:
                    if IS_PYTHON_2:
                        content = unicode(content)
                    file.write(content)
            except IOError as e:
                raise RuntimeError("Error outputting to file '%s':\n%s" % (
                    file_path, e))
        return json

    @keyword(name=None, tags=("I/O",))
    def rest_instances(self, file_path=None, sort_keys=False):
        if not file_path:
            outputdir_path = BuiltIn().get_variable_value("${OUTPUTDIR}")
            if self.request['netloc']:
                file_path = path.join(outputdir_path,
                    self.request['netloc']) + '.json'
            else:
                file_path = path.join(outputdir_path, "instances") + '.json'
        sort_keys = self._input_boolean(sort_keys)
        content = dumps(self.instances, ensure_ascii=False, indent=4,
                        separators=(',', ': '), sort_keys=sort_keys)
        try:
            with open(file_path, 'w', encoding="utf-8") as file:
                if IS_PYTHON_2:
                    content = unicode(content)
                file.write(content)
        except IOError as e:
            raise RuntimeError("Error exporting instances " +
                "to file '%s':\n%s" % (file_path, e))
        return self.instances

    ### Internal methods

    def _request(self, endpoint, request, validate=True):
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        if not endpoint.startswith(('http://', 'https://')):
            base_url = self.request['scheme'] + "://" + self.request['netloc']
            if not endpoint.startswith('/'):
                endpoint = "/" + endpoint
            endpoint = urljoin(base_url, self.request['path']) + endpoint
        request['url'] = endpoint
        url_parts = urlparse(request['url'])
        request['scheme'] = url_parts.scheme
        request['netloc'] = url_parts.netloc
        request['path'] = url_parts.path
        try:
            response = client(request['method'], request['url'],
                              params=request['query'],
                              json=request['body'],
                              headers=request['headers'],
                              proxies=request['proxies'],
                              cert=request['cert'],
                              timeout=tuple(request['timeout']),
                              allow_redirects=request['allowRedirects'],
                              verify=request['sslVerify'])
        except SSLError as e:
            raise AssertionError("%s to %s SSL certificate verify failed:\n%s" %
                (request['method'], request['url'], e))
        except Timeout as e:
            raise AssertionError("%s to %s timed out:\n%s" % (
                request['method'], request['url'], e))
        utc_datetime = datetime.now(tz=utc)
        request['timestamp'] = {
            'utc': utc_datetime.isoformat(),
            'local': utc_datetime.astimezone(get_localzone()).isoformat()
        }
        if validate and self.spec:
            self._assert_spec(self.spec, response)
        instance = self._instantiate(request, response, validate)
        self.instances.append(instance)
        return instance

    def _instantiate(self, request, response, validate_schema=True):
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text
        response = {
            'seconds': response.elapsed.microseconds / 1000 / 1000,
            'status': response.status_code,
            'body': response_body,
            'headers': dict(response.headers)
        }
        schema = deepcopy(self.schema)
        request_properties = schema['properties']['request']['properties']
        response_properties = schema['properties']['response']['properties']
        if validate_schema:
            if request_properties:
                self._validate_schema(request_properties, request)
            if response_properties:
                self._validate_schema(response_properties, response)
        request_properties['body'] = self._new_schema(request['body'])
        response_properties['query'] = self._new_schema(request['query'])
        response_properties['body'] = self._new_schema(response['body'])
        if 'exampled' in schema and schema['exampled']:
            self._generate_schema_examples(schema, response)
        return {
            'request': request,
            'response': response,
            'schema': schema,
            'spec': self.spec
        }

    def _assert_spec(self, spec, response):
        request = response.request
        try:
            validate_api_call(spec, raw_request=request, raw_response=response)
        except ValueError as e:
            raise AssertionError(e)

    def _validate_schema(self, schema, json_dict):
        for field in schema:
            self._assert_schema(schema[field], json_dict[field])

    def _assert_schema(self, schema, reality):
        try:
            if "draft-06" in self.schema['$schema']:
                 validator = Draft6Validator(schema,
                    format_checker=FormatChecker())
            else:
                validator = Draft4Validator(schema,
                    format_checker=FormatChecker())
            validator.validate(reality)
        except ValidationError as e:
            raise AssertionError(e)

    def _new_schema(self, value):
        builder = SchemaBuilder(schema_uri=False)
        builder.add_object(value)
        return builder.to_schema()

    def _generate_schema_examples(self, schema, response):
        body = response['body']
        schema = schema['properties']['response']['properties']['body']
        if isinstance(body, (dict)):
            for field in body:
                schema['properties'][field]['example'] = body[field]
        elif isinstance(body, (list)):
            schema['example'] = body

    def _find_by_field(self, field, return_schema=True, print_found=True):
        last_instance = self._last_instance_or_error()
        schema = None
        paths = []
        if field.startswith("$"):
            value = last_instance['response']['body']
            if return_schema:
                res_schema = last_instance['schema']['properties']['response']
                schema = res_schema['properties']['body']
            if field == "$":
                paths = []
            else:
                try:
                    query = parse_jsonpath(field)
                except Exception as e:
                    raise RuntimeError("Invalid JSONPath query '%s':\n%s" % (
                        field, e))
                matches = [str(match.full_path) for match in query.find(value)]
                if not matches:
                    raise AssertionError("JSONPath query '%s' " % (field) +
                        "did not match anything.")
                for match in matches:
                    path = match.replace("[", "").replace("]", "").split('.')
                    paths.append(path)
        else:
            value = last_instance
            if return_schema:
                schema = last_instance['schema']['properties']
            path = field.split()
            paths.append(path)
        return [self._find_by_path(field, path, value, schema, print_found)
                for path in paths]

    def _last_instance_or_error(self):
        try:
            return self.instances[-1]
        except IndexError:
            raise RuntimeError("No instances: No requests made, " +
                "and no previous instances loaded in the library import.")

    def _find_by_path(self, field, path, value, schema=None, print_found=True):
        for key in path:
            try:
                value = self._value_by_key(value, key)
            except (KeyError, TypeError):
                if print_found:
                    self.log_json(value,
                        "\n\nProperty '%s' does not exist in:" % (key))
                raise AssertionError(
                    "\nExpected property '%s' was not found." % (field))
            except IndexError:
                if print_found:
                    self.log_json(value,
                        "\n\nIndex '%s' does not exist in:" % (key))
                raise AssertionError(
                    "\nExpected index '%s' did not exist." % (field))
            if schema:
                schema = self._schema_by_key(schema, key, value)
        found = {
            'path': path,
            'reality': value,
            'schema': schema
        }
        return found

    def _value_by_key(self, json, key):
        try:
            return json[int(key)]
        except ValueError:
            return json[key]

    def _schema_by_key(self, schema, key, value):
        if 'properties' in schema:
            schema = schema['properties']
        elif 'items' in schema:
            if isinstance(schema['items'], (dict)):
                schema['items'] = [schema['items']]
            new_schema = self._new_schema(value)
            try:
                return schema['items'][schema['items'].index(new_schema)]
            except ValueError:
                schema['items'].append(new_schema)
                return schema['items'][-1]
        if key not in schema:
            schema[key] = self._new_schema(value)
            if self._should_add_examples():
                schema[key]['example'] = value
        return schema[key]

    def _should_add_examples(self):
        schema = self._last_instance_or_error()['schema']
        return 'exampled' in schema and schema['exampled']

    def _set_type_validations(self, json_type, schema, validations):
        if validations:
            if "draft-06" in self.schema['$schema']:
                schema_version = "draft-06"
            else:
                schema_version = "draft-04"
            kws = list(SCHEMA_KEYWORDS['common'][schema_version])
            kws.extend(SCHEMA_KEYWORDS[json_type][schema_version])
        for validation in validations:
            if validation not in kws:
                raise RuntimeError("Unknown JSON Schema (%s)" % (
                    schema_version) + " validation keyword " +
                "for %s:\n%s" % (json_type, validation))
            schema[validation] = self.input(validations[validation])
        schema.update({ "type": json_type })
