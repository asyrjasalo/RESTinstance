from io import open  # required for Python 2
from .compat import IS_PYTHON_2, STRING_TYPES

from pytz import utc
from tzlocal import get_localzone

from copy import deepcopy
from datetime import datetime
from json import dumps
from os import path, getcwd

if IS_PYTHON_2:
    from urlparse import parse_qs, urlparse
else:
    from urllib.parse import parse_qs, urlparse

from flex.core import validate_api_call
from genson import Schema
from jsonschema import Draft4Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from requests import request as client
from requests.exceptions import Timeout

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
    def head(self, endpoint, timeout=None, allow_redirects=None, validate=True):
        request = deepcopy(self.request)
        request['method'] = "HEAD"
        request['endpoint'] = endpoint
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    @keyword
    def options(self, endpoint, timeout=None, allow_redirects=None,
                validate=True):
        request = deepcopy(self.request)
        request['method'] = "OPTIONS"
        request['endpoint'] = endpoint
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    @keyword
    def get(self, endpoint, query=None, timeout=None, allow_redirects=None,
            validate=True):
        request = deepcopy(self.request)
        request['method'] = "GET"
        request['query'] = {}
        query_in_url = parse_qs(urlparse(endpoint).query)
        if query_in_url:
            request['query'].update(query_in_url)
            endpoint = endpoint.rsplit('?', 1)[0]
        if query:
            request['query'].update(self._input_object(query))
        request['endpoint'] = endpoint
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    @keyword
    def post(self, endpoint, body=None, timeout=None, allow_redirects=None,
             validate=True):
        request = deepcopy(self.request)
        request['method'] = "POST"
        request['endpoint'] = endpoint
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    @keyword
    def put(self, endpoint, body=None, timeout=None, allow_redirects=None,
            validate=True):
        request = deepcopy(self.request)
        request['method'] = "PUT"
        request['endpoint'] = endpoint
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    @keyword
    def patch(self, endpoint, body=None, timeout=None, allow_redirects=None,
              validate=True):
        request = deepcopy(self.request)
        request['method'] = "PATCH"
        request['endpoint'] = endpoint
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    @keyword
    def delete(self, endpoint, timeout=None, allow_redirects=None,
               validate=True):
        request = deepcopy(self.request)
        request['method'] = "DELETE"
        request['endpoint'] = endpoint
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        return self._request(request, validate)['response']

    # Assertions

    @keyword
    def missing(self, field):
        try:
            found = self._find_by_field(field, print_found=False)
        except AssertionError:
            return None
        self.log_json(found['reality'],
            "\n\nExpected '%s' to not exist, but it is:\n%s" % (field))
        raise AssertionError("Expected '%s' to not exist, but it does." % (
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
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("integer", schema, validations)
        if enum:
            schema['enum'] = [self._input_integer(value) for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def number(self, field, *enum, **validations):
        found = self._find_by_field(field)
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("number", schema, validations)
        if enum:
            schema['enum'] = [self._input_number(value) for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def string(self, field, *enum, **validations):
        found = self._find_by_field(field)
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("string", schema, validations)
        if enum:
            schema['enum'] = [self._input_string(value) for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def object(self, field, *enum, **validations):
        found = self._find_by_field(field)
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("object", schema, validations)
        if enum:
            schema['enum'] = [self._input_object(value) for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    @keyword
    def array(self, field, *enum, **validations):
        found = self._find_by_field(field)
        schema = found['schema']
        reality = found['reality']
        skip = self._input_boolean(validations.pop('skip', False))
        self._set_type_validations("array", schema, validations)
        if enum:
            schema['enum'] = [self._input_array(value) for value in enum]
        if not skip:
            self._assert_schema(schema, reality)
        return reality

    # IO keywords

    # Is stateless
    @keyword
    def input(self, value_or_jsonfile):
        if value_or_jsonfile is None:
            return None
        if not isinstance(value_or_jsonfile, STRING_TYPES):
            return self._input_json_from_non_string(value_or_jsonfile)
        if path.isfile(value_or_jsonfile):
            return self._input_json_from_file(value_or_jsonfile)
        value = value_or_jsonfile
        try:
            return self._input_json_as_string(value)
        except ValueError:
            return self._input_string(value)

    # Operates on the (last) request state
    @keyword
    def output(self, what=None, file_path=None, append=False):
        if not what:
            try:
                json = self.instances[-1]
            except IndexError:
                raise RuntimeError("No instance to output: " +
                    "No requests done thus no responses gotten yet, " +
                    "and no previous instances loaded in the library settings.")
            if not file_path:
                return self.log_json(json, "\n\nJSON for the instance is:\n")
        else:
            json = self._find_by_field(what, return_schema=False)['reality']
            if not file_path:
                return self.log_json(json, "\n\nJSON for '%s' is:\n" % (what))
        content = dumps(json, ensure_ascii=False, indent=4,
                        separators=(',', ':' ))
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

    # Operates on the suite level state
    @keyword
    def rest_instances(self, file_path=None):
        if not file_path:
            outputdir_path = BuiltIn().get_variable_value("${OUTPUTDIR}")
            hostname = urlparse(self.url).netloc
            file_path = path.join(outputdir_path, hostname) + '.json'
        content = dumps(self.instances, ensure_ascii=False, indent=4,
                        separators=(',', ': '))
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

    def _request(self, request, validate=True):
        if request['endpoint'].endswith('/'):
            request['endpoint'] = request['endpoint'][:-1]
        if request['endpoint'].startswith(('http://', 'https://')):
            full_url = request['endpoint']
        else:
            if not request['endpoint'].startswith('/'):
                request['endpoint'] = '/' + request['endpoint']
            full_url = self.url + request['endpoint']
        try:
            response = client(request['method'], full_url,
                              params=request['query'],
                              json=request['body'],
                              headers=request['headers'],
                              proxies=request['proxies'],
                              cert=request['cert'],
                              timeout=tuple(request['timeout']),
                              allow_redirects=request['allowRedirects'],
                              verify=request['sslVerify'])
        except Timeout as e:
            raise AssertionError("%s request to %s timed out:\n%s" % (
                request['method'], full_url, e))
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
            'status': response.status_code,
            'seconds': response.elapsed.microseconds / 1000 / 1000,
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
        return Schema().add_object(value).to_dict()

    def _generate_schema_examples(self, schema, response):
        body = response['body']
        schema = schema['response']['body']
        if isinstance(body, (dict)):
            for field in body:
                schema['properties'][field]['example'] = body[field]
        elif isinstance(body, (list)):
            schema['example'] = body

    def _find_by_field(self, field, return_schema=True, print_found=True):
        keys = field.split()
        try:
            value = self.instances[-1]
        except IndexError:
            raise RuntimeError("Nothing to validate against: " +
                "No requests done thus no responses gotten yet, " +
                "and no previous instances loaded in the library settings.")
        schema = value['schema']
        if 'exampled' in schema and schema['exampled']:
            add_example = True
        else:
            add_example = False
        for key in keys:
            try:
                value = self._value_by_key(value, key)
            except (KeyError, TypeError):
                if print_found:
                    self.log_json(value,
                        "\n\nProperty '%s' does not exist in:\n" % (key))
                raise AssertionError(
                    "\nExpected property '%s' was not found." % (field))
            except IndexError:
                if print_found:
                    self.log_json(value,
                        "\n\nIndex '%s' does not exist in:\n" % (key))
                raise AssertionError(
                    "\nExpected index '%s' did not exist." % (field))
            if return_schema:
                schema = self._schema_by_key(schema, key, value, add_example)
        found = {
            'keys': keys,
            'reality': value
        }
        if return_schema:
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
                raise RuntimeError("Unknown JSON Schema (%s)" % (
                    self.schema['version']) + " validation keyword " +
                "for %s:\n%s" % (json_type, validation))
            schema[validation] = self.input(validations[validation])
        schema.update({ "type": json_type })
