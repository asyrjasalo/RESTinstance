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
from jsonschema import Draft4Validator, FormatChecker
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

    # Settings

    @keyword
    def set_client_cert(self, cert):
        self.request['cert'] = self._input_client_cert(cert)
        return self.request['cert']

    @keyword
    def set_headers(self, headers):
        self.request['headers'].update(self._input_object(headers))
        return self.request['headers']

    # Expectations

    @keyword
    def expect_request(self, schema, replace=False):
        if self._input_boolean(replace):
            self.schema['response'] = self._input_object(schema)
        else:
            self.schema['request'].update(self._input_object(schema))
        return self.schema['request']

    @keyword
    def expect_response(self, schema, replace=False):
        if self._input_boolean(replace):
            self.schema['response'] = self._input_object(schema)
        else:
            self.schema['response'].update(self._input_object(schema))
        return self.schema['response']

    @keyword
    def expect_spec(self, spec, replace=False):
        if self._input_boolean(replace):
            self.spec = self._input_object(spec)
        else:
            self.spec.update(self._input_object(spec))
        return self.spec

    @keyword
    def clear_expectations(self):
        self.schema['request'] = {}
        self.schema['response'] = {}
        return self.schema

    # Requests

    @keyword
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

    @keyword
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

    @keyword
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

    @keyword
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

    @keyword
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

    @keyword
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

    @keyword
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

    # Assertions

    @keyword
    def missing(self, field):
        try:
            matches = self._find_by_field(field, print_found=False)
        except AssertionError:
            return
        for found in matches:
            self.log_json(found['reality'],
                "\n\nExpected '%s' to not exist, but it is:" % (field))
        raise AssertionError("Expected '%s' to not exist, but it does." % (
            field))

    @keyword
    def null(self, field, **validations):
        values = []
        for found in self._find_by_field(field):
            reality = found['reality']
            schema = { "type": "null" }
            skip = self._input_boolean(validations.pop('skip', False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword
    def boolean(self, field, value=None, **validations):
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

    @keyword
    def integer(self, field, *enum, **validations):
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

    @keyword
    def number(self, field, *enum, **validations):
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

    @keyword
    def string(self, field, *enum, **validations):
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

    @keyword
    def object(self, field, *enum, **validations):
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

    @keyword
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

    # IO keywords

    @keyword
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

    @keyword
    def output(self, what="", file_path=None, append=False,
               sort_keys=False):
        message = "\n%s as JSON is:" % (what.__class__.__name__)
        if what == "":
            message = "\n\nThe current instance as JSON is:"
            try:
                json = self._last_instance_or_error()
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

    @keyword
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
        if validate_schema:
            if schema['request']:
                self._validate_schema(schema['request'], request)
            if schema['response']:
                self._validate_schema(schema['response'], response)
        schema['request']['body'] = self._new_schema(request['body'])
        schema['request']['query'] = self._new_schema(request['query'])
        schema['response']['body'] = self._new_schema(response['body'])
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
            schema_version = self.schema['version']
            if schema_version == 'draft04':
                validator = Draft4Validator(schema,
                    format_checker=FormatChecker())
            else:
                raise RuntimeError("Unknown JSON Schema version " +
                    "was given:\n%s" % (schema_version))
            validator.validate(reality)
        except ValidationError as e:
            raise AssertionError(e)

    def _new_schema(self, value):
        builder = SchemaBuilder(schema_uri=False)
        builder.add_object(value)
        return builder.to_schema()

    def _generate_schema_examples(self, schema, response):
        body = response['body']
        schema = schema['response']['body']
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
                schema = last_instance['schema']['response']['body']
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
                schema = last_instance['schema']
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
            kws = list(SCHEMA_KEYWORDS['common'][self.schema['version']])
            kws.extend(SCHEMA_KEYWORDS[json_type][self.schema['version']])
        for validation in validations:
            if validation not in kws:
                raise RuntimeError("Unknown JSON Schema (%s)" % (
                    self.schema['version']) + " validation keyword " +
                "for %s:\n%s" % (json_type, validation))
            schema[validation] = self.input(validations[validation])
        schema.update({ "type": json_type })
