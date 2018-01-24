from copy import deepcopy
from datetime import datetime, timezone
from json import dump
from os import path, getcwd
from urllib.parse import parse_qs, urlparse

from flex.core import validate_api_call
from genson import Schema
from jsonschema import Draft4Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from requests import request as client
from requests.exceptions import Timeout
from requests.packages.urllib3 import disable_warnings

from robot.api import logger
from robot.api.deco import keyword

from .schema_keywords import SCHEMA_KEYWORDS


class Keywords(object):

    def get_keyword_names(self):
        return [name for name in dir(self) if hasattr(getattr(self, name),
            'robot_name')]

    ### Settings

    @keyword
    def set_basic_auth(self, auth):
        self.request['auth'] = self._input_list(auth)
        return self.request['auth']

    @keyword
    def set_client_cert(self, cert):
        self.request['cert'] = self._input_client_cert(cert)
        return self.request['cert']

    @keyword
    def set_headers(self, headers):
        self.request['headers'].update(self._input_object(headers))
        return self.request['headers']

    ### Expectations

    @keyword
    def expect_request(self, schema):
        self.schema['request'].update(self._input_object(schema))
        return self.schema['request']

    @keyword
    def expect_response(self, schema):
        self.schema['response'].update(self._input_object(schema))
        return self.schema['response']

    @keyword
    def expect_spec(self, spec):
        self.spec = self.input(spec)
        return self.spec

    @keyword
    def clear_expectations(self):
        self.schema['request'] = {}
        self.schema['response'] = {}
        return self.schema

    ### HTTP methods

    @keyword
    def head(self, endpoint, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "HEAD"
        request['endpoint'] = endpoint
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    @keyword
    def options(self, endpoint, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "OPTIONS"
        request['endpoint'] = endpoint
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    @keyword
    def get(self, endpoint, query=None, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "GET"
        request['query'] = {}
        query_in_url = parse_qs(urlparse(endpoint).query)
        if query_in_url:
            request['query'].update(query_in_url)
            endpoint = endpoint.rsplit('?', 1)[0]
        if query:
            request['query'].update(self._input_object(query))
        request['endpoint'] = endpoint
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    @keyword
    def post(self, endpoint, body=None, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "POST"
        request['endpoint'] = endpoint
        request['body'] = self.input(body)
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    @keyword
    def put(self, endpoint, body=None, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "PUT"
        request['endpoint'] = endpoint
        request['body'] = self.input(body)
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    @keyword
    def patch(self, endpoint, body=None, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "PATCH"
        request['endpoint'] = endpoint
        request['body'] = self.input(body)
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    @keyword
    def delete(self, endpoint, timeout=None, allow_redirects=True):
        request = {}
        request['method'] = "DELETE"
        request['endpoint'] = endpoint
        request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout:
            request['timeout'] = self._input_timeout(timeout)
        return self._request(**request)['response']

    ### Assertions

    @keyword
    def missing(self, field):
        try:
            found = self._find_by_field(field, show_found=False)
        except AssertionError:
            return None
        self.print(found['reality'],
            "\n\nExpected '{}' to not exist, but it is:\n{}".format(field))
        raise AssertionError("Expected '{}' to not exist, but it does.".format(
            field))

    @keyword
    def null(self, field, **validations):
        found = self._find_by_field(field)
        reality = found['reality']
        schema = { "type": "null" }
        skip = self._input_boolean(validations.pop('skip', False))
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def boolean(self, field, value=None, **validations):
        found = self._find_by_field(field)
        keys = found['keys']
        reality = found['reality']
        schema = { "type": "boolean" }
        if value is not None:
            schema['enum'] = [self._input_boolean(value)]
        skip = self._input_boolean(validations.pop('skip', False))
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def integer(self, field, *enum, **validations):
        found = self._find_by_field(field)
        keys = found['keys']
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("integer", schema, validations)
        if enum:
            enum = [self._input_integer(value) for value in enum]
            schema['enum'] = [value for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def number(self, field, *enum, **validations):
        found = self._find_by_field(field)
        keys = found['keys']
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("number", schema, validations)
        if enum:
            enum = [self._input_number(value) for value in enum]
            schema['enum'] = [value for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def string(self, field, *enum, **validations):
        found = self._find_by_field(field)
        keys = found['keys']
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("string", schema, validations)
        if enum:
            enum = [self._input_string(value) for value in enum]
            schema['enum'] = [value for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def object(self, field, *enum, **validations):
        found = self._find_by_field(field)
        keys = found['keys']
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("object", schema, validations)
        if enum:
            enum = [self._input_object(value) for value in enum]
            schema['enum'] = [value for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def array(self, field, *enum, **validations):
        found = self._find_by_field(field)
        keys = found['keys']
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("array", schema, validations)
        if enum:
            enum = [self._input_array(value) for value in enum]
            schema['enum'] = [value for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def input(self, what):
        if not isinstance(what, str):
            return self._input_non_string(what)
        if path.isfile(what):
            return self._input_json_file(what)
        try:
            return self._input_json_string(what)
        except RuntimeError:
            return self._input_string(what)

    @keyword
    def output(self, what=None, file_path=None):
        if not what:
            try:
                json = self.instances[-1]
            except IndexError:
                raise RuntimeError("No instance to output " +
                    "before a request is made.")
            if not file_path:
                return self.print(json, "\n\nJSON for the instance is:\n")
        else:
            json = self._find_by_field(what, also_schema=False)['reality']
            if not file_path:
                return self.print(json, "\n\nJSON for '{}' is:\n".format(what))
        try:
            with open(path.join(getcwd(), file_path), 'w') as file:
                dump(json, file, ensure_ascii=False, indent=4)
        except IOError as e:
            raise RuntimeError("Error outputting to file '{}':\n{}".format(
                file_path, e))
        return json

    @keyword
    def rest_instances(self, file_path):
        instances = {
            "url": self.url,
            "instances": self.instances
        }
        try:
            with open(path.join(getcwd(), file_path), 'w') as file:
                dump(instances, file, ensure_ascii=False, indent=4)
        except IOError as e:
            raise RuntimeError("Error exporting instances " +
                "to file '{}':\n{}".format(file_path, e))
        return instances

    def _request(self, **fields):
        request = deepcopy(self.request)
        request.update(fields)
        if request['endpoint'].endswith('/'):
            request['endpoint'] = request['endpoint'][:-1]
        if request['endpoint'].startswith(('http://', 'https://')):
            full_url = request['endpoint']
        else:
            if not request['endpoint'].startswith('/'):
                request['endpoint'] = '/' + request['endpoint']
            full_url = self.url + request['endpoint']
        if not request['sslVerify']:
            disable_warnings()
        auth = tuple(request['auth']) if request['auth'] else None
        timeout = tuple(request['timeout']) if request['timeout'] else None
        try:
            response = client(request['method'], full_url,
                              params=request['query'],
                              json=request['body'],
                              headers=request['headers'],
                              proxies=request['proxies'],
                              auth=auth,
                              cert=request['cert'],
                              timeout=timeout,
                              allow_redirects=request['allowRedirects'],
                              verify=request['sslVerify'])
        except Timeout as e:
            raise AssertionError("{} request to {} timed out:\n{}".format(
                request['method'], full_url, e))
        utc_datetime = datetime.now(timezone.utc)
        request['timestamp'] = {
            'utc': utc_datetime.isoformat(),
            'local': utc_datetime.astimezone().isoformat()
        }
        return self._instantiate(request, response)

    def _instantiate(self, request, response):
        if self.spec:
            self._assert_spec(self.spec, response)
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text
        response = {
            'status': response.status_code,
            'seconds': response.elapsed.microseconds / 1000 / 1000,
            'body': response_body,
            'headers': dict(response.headers)
        }
        schema = deepcopy(self.schema)
        if schema['request']:
            self._validate_schema(schema['request'], request)
        if schema['response']:
            self._validate_schema(schema['response'], response)
        if 'body' in response:
            schema['response']['body'] = self._new_schema(response['body'])
        if 'body' in request:
            schema['request']['body'] = self._new_schema(request['body'])
        if 'query' in request:
            schema['request']['query'] = self._new_schema(request['query'])
        if 'exampled' in schema and schema['exampled']:
            self._generate_schema_examples(schema, response)
        instance = {
            'request': request,
            'response': response,
            'schema': schema,
            'spec': self.spec
        }
        self.instances.append(instance)
        return instance

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
                    "was given:\n{}".format(schema_version))
            validator.validate(reality)
        except ValidationError as e:
            raise AssertionError(e)

    def _new_schema(self, value):
        return Schema().add_object(value).to_dict()

    def _generate_schema_examples(self, schema, response):
        body = response['body']
        schema = schema['response']['body']
        if isinstance(body, dict):
            for field in body:
                schema['properties'][field]['example'] = body[field]
        elif isinstance(body, list):
            schema['example'] = body

    def _find_by_field(self, field, also_schema=True, show_found=True):
        keys = field.split()
        value = self.instances[-1]
        schema = value['schema']
        if 'exampled' in schema and schema['exampled']:
            add_example = True
        else:
            add_example = False
        for key in keys:
            try:
                value = self._value_by_key(value, key)
            except (KeyError, TypeError):
                if show_found:
                    self.print(value,
                        "\n\nProperty '{}' does not exist in:\n".format(key))
                raise AssertionError(
                    "\nExpected property '{}' was not found.".format(field))
            except IndexError:
                if show_found:
                    self.print(value,
                        "\n\nIndex '{}' does not exist in:\n".format(key))
                raise AssertionError(
                    "\nExpected index '{}' did not exist.".format(field))
            if also_schema:
                schema = self._schema_by_key(schema, key, value, add_example)
        found = {
            'keys': keys,
            'reality': value
        }
        if also_schema:
            found.update({ 'schema': schema })
        return found

    def _value_by_key(self, json, key):
        try:
            return json[int(key)]
        except ValueError:
            return json[key]

    def _schema_by_key(self, schema, key, value, add_example=False):
        if key not in schema:
            if 'properties' in schema:
                schema = schema['properties']
            elif 'items' in schema:
                schema = schema['items']
            if key not in schema:
                schema[key] = self._new_schema(value)
            if add_example:
                schema[key]['example'] = value
        return schema[key]

    def _set_type_validations(self, json_type, schema, validations):
        if validations:
            kws = list(SCHEMA_KEYWORDS['common'][self.schema['version']])
            kws.extend(SCHEMA_KEYWORDS[json_type][self.schema['version']])
        for validation in validations:
            if validation not in kws:
                raise RuntimeError("Unknown JSON Schema ({})".format(
                    self.schema['version']) + " validation keyword " +
                "for {}:\n{}".format(json_type, validation))
            schema[validation] = self.input(validations[validation])
        schema.update({ "type": json_type })
