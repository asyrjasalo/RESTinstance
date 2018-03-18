RESTinstance
============

`Robot Framework <https://robotframework.org>`__ test library for (RESTful) JSON APIs

Why?
----

1. **RESTinstance relies on Robot Framework's language-agnostic,
   natural language syntax for API tests.** It is not tied to any
   particular programming language nor development framework. Using
   RESTinstance requires little, if any, programming knowledge. It
   builts on long-term technologies with well established communities,
   such as HTTP, JSON (Schema), OpenAPI and Robot Framework.

2. **It validates JSON using JSON Schema, guiding you to write API tests
   to base on constraints** rather than on specific values (e.g. "email
   must be valid" vs "email is foo@bar.com"). This approach reduces test
   maintenance when the values responded by the API are prone to change.
   Although values are not required, you can still test whenever they
   make sense (e.g. GET response body from one endpoint, then POST some
   of its values to another endpoint).

3. **It generates JSON Schema for requests and responses automatically,
   and the schema gets more accurate by you writing tests.** The schema
   is a contract between different teams, or functions (backend,
   frontend, partners), to agree on what kind of data the API handles.
   Additionally, you can mark validations to be skipped and rather use
   the tests to define how the API should work - then the schema also
   acts as a design. The schema can be further extended to an OpenAPI
   specification (manually for now, generating also this is planned),
   which RESTinstance can also test requests and responses against. This
   leads to very clean looking tests.

Installation
------------

Python:
~~~~~~~

::

    pip install --upgrade RESTinstance

The package is hosted in
`PyPi <https://pypi.python.org/pypi/RESTinstance>`__.

Using Docker
~~~~~~~~~~~~

If you have Docker available, prefer
`rfdocker <https://github.com/asyrjasalo/rfdocker>`__ and just add
``RESTinstance`` to your ``requirements.txt``.

Alternatively, a ready image is available at
`DockerHub <https://hub.docker.com/r/asyrjasalo/restinstance/>`__.

Usage
-----

See `keyword
documentation <https://github.com/asyrjasalo/RESTinstance/tree/master/docs/REST.html>`__.

The most common use cases for RESTinstances are:

1. **Testing for JSON types and formats using JSON Schema validations.**
   For examples, see ``tests/validations.robot``.

2. **Flow-driven API tests, i.e. multiple APIs are called for the
   result.** For examples, see ``tests/methods.robot``.

3. **Testing API requests and responses against a schema or a
   specification.** For examples testing against JSON schemas, see
   ``tests/schema.robot`` and for testing against Swagger 2.0
   specification, see ``tests/spec.robot``.

(TODO: embed examples here)

Development
-----------

The issues and requests are tracked in
`GitHub <https://github.com/asyrjasalo/RESTinstance/issues>`__. We
kindly do take pull requests (please mention if you do not want to be
listed as contributors).

Running tests
~~~~~~~~~~~~~

Docker is mandatory for running the library's own tests:

::

    ./test

To run on python 2:

::

    BUILD_ARGS="-f Dockerfile.python2" ./test

System under test
~~~~~~~~~~~~~~~~~

The test API is implemented by
`mounterest <https://github.com/asyrjasalo/mounterest>`__, which in turn
builds on `mountebank <http://www.mbtest.org>`__.

In the scope of library's tests, mounterest acts as a HTTP proxy to
`Typicode's live JSON server <jsonplaceholder.typicode.com>`__ and uses
mountebank's injections to enrich responses slightly, so that they
better match to this library's testing needs. Particularly, it allows us
to test the library with non-safe HTTP methods (POST, PUT, PATCH,
DELETE) by mimicking their changes in the state only, instead of trying
to issue them on the live server. The state is cleared between the test
runs.

Credits
-------

RESTinstance is licensed under Apache License 2.0.

RESTinstance was originally written by Anssi Syrjäsalo, and was
initially presented at `RoboCon 2018 <https://robocon.io>`__.

Python libraries
~~~~~~~~~~~~~~~~

We use the following Python libraries and tools under the hood:

-  `GenSON <https://github.com/wolverdude/GenSON>`__, by Jon
   "wolverdude" Wolverton, for JSON Schema generation
-  `Flex <https://github.com/pipermerriam/flex>`__, by Piper Merriam,
   for Swagger 2.0 validation
-  `jsonschema <https://github.com/Julian/jsonschema>`__, by Julian
   Berman, for JSON Schema draft-04 validation
-  `requests <https://github.com/requests/requests>`__, by Kenneth
   Reitz, for Python HTTP requests

See ``requirements.txt`` for a full list of all the (direct)
dependencies.