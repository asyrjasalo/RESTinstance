Starting from zero
==================

This tutorial is organized so that each part introduces a few new topics,
usually building directly on top of the previous. Following the numbered order,
it should gradually become more clear where RESTinstance targets to guide you.

The library builds on JSON Schema validation keywords, but to keep this guide focused, we only use a handful of them in the examples. Similarly, for JSONPath,
to unlock the full power, accompany this guide with the official reference.

Tip (#1): Bookmark reference pages to speed up finding things when writing tests.

- 0_hello.rst

  - library init
  - url
  - ssl verify

- 1_http.rst

  - methods
  - output response body
  - output (to file)

- 2_auth.rst

  - set headers
  - headers per request
  - set client cert

- 3_types.rst

  - keywords
  - properties
  - jsonpath

- 4_values.rst

  - enums (+ RF variables)
  - json files
  - stateful APIs (reusing response)

- 5_validations.rst

  - draft04/draft06 basics
  - validationkws per type
  - output schema

- 6_schemas.rst

  - output schema to file
  - expect response, clear expectations
  - exampled: on/off

- 7_models.rst

  - merging schemas
  - test setup -> suite setup
  - generating test data

- 8_specs.rst

  - swagger/openapi3: format, designing, documentation, future
  - expect spec
  - validate=false

- 9_instances.rst

  - Rest Instances
  - spec + data = service
  - collecting history, post-processing, ideas
