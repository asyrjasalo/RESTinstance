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
   must be valid" vs "email is foo\@bar.com"). This approach reduces test
   maintenance when the values responded by the API are prone to change.
   Although values are not required, you can still test whenever they
   make sense (e.g. GET response body from one endpoint, then POST some
   of its values to another endpoint).

3. **It generates JSON Schema for requests and responses automatically,
   and the schema gets more accurate by your tests.** The schema
   is a contract between different teams, or functions (backend,
   frontend, test developers), to agree on what kind of data the API handles.
   Additionally, you can mark validations to be skipped and rather use
   the tests to define how the API should work - then the schema also
   acts as a design. The schema can be further extended to an OpenAPI
   specification (manually for now, generating also this is planned),
   which RESTinstance can also test requests and responses against.
   This leads to very clean looking tests.


Installation
------------

Python
~~~~~~~
On 3.x and 2.7, you can install `the package from PyPi <https://pypi.python.org/pypi/RESTinstance>`__:

::

    pip install --upgrade RESTinstance

Docker
~~~~~~~

`The image <https://hub.docker.com/r/asyrjasalo/restinstance/tags>`__ has Python 3.6 and `the latest Robot Framework <https://pypi.python.org/pypi/robotframework/3.0.2>`__:

::

   docker pull asyrjasalo/restinstance
   docker run --rm -ti --env HOST_UID=$(id -u) --env HOST_GID=$(id -g) \
     --volume "$PWD/tests":/home/robot/tests \
     --volume "$PWD/results":/home/robot/results \
     asyrjasalo/restinstance tests

rfdocker
~~~~~~~~
If you are already using `rfdocker <https://github.com/asyrjasalo/rfdocker>`__,
just add ``RESTinstance`` to your ``requirements.txt`` and remove the
commented lines in ``Dockerfile``. It will be installed automatically
the next time you run ``./rfdocker``.


Usage
-----

Tip: You can run this README.rst as a test with Robot Framework.

The most common use cases for library are:

1. **Writing the classic value based API tests**

.. code:: robotframework

    *** Settings ***
    Library         REST              https://jsonplaceholder.typicode.com

    *** Variables ***
    ${json}=        { "id": 11, "name": "Gil Alexander" }
    &{dict}=        name=Julie Langford

    *** Test Cases ***
    GET existing users
        GET         /users?limit=5
        Array       response body
        Object      response body 0
        Integer     response body 0 id        1
        [Teardown]  Output  response body 0

    GET an existing user
        GET         /users/1
        Integer     response body id          1
        String      response body name        Leanne Graham

    POST with valid params to create an user
        POST        /users                    ${json}
        Integer     response status           201

    PUT with valid params to update existing
        PUT         /users/2                  { "isCoding": true }
        Boolean     response body isCoding    true
        PUT         /users/2                  { "sleep": null }
        Null        response body sleep
        PUT         /users/2                  { "pockets": "", "money": 0.02 }
        String      response body pockets     ${EMPTY}
        Number      response body money       0.02
        Missing     response body moving

    PATCH with valid params and using response as the new payload
        &{res}=     GET   /users/3
        String      response body name        Clementine Bauch
        PATCH       /users/4                  { "name": "${res.body['name']}" }
        String      response body name        Clementine Bauch
        PATCH       /users/5                  ${dict}
        String      response body name        ${dict.name}

    DELETE existing successfully
        DELETE      /users/6
        Integer     response status           200    202     204


2. **Testing for JSON types and constraints using JSON Schema validations.**
   `Examples <https://github.com/asyrjasalo/RESTinstance/blob/master/tests/validations.robot>`__.


3. **Testing API requests and responses against a schema or a specification.**
   `Examples for testing against JSON schema <https://github.com/asyrjasalo/RESTinstance/blob/master/tests/schema.robot>`__ and `examples for testing against Swagger 2.0 specification <https://github.com/asyrjasalo/RESTinstance/blob/master/tests/spec.robot>`__.

See `keyword documentation <https://asyrjasalo.github.io/RESTinstance>`__.


Development
-----------

Bug reports and feature requests are tracked in
`GitHub <https://github.com/asyrjasalo/RESTinstance/issues>`__.

We do respect pull request(er)s. Please mention if you do not want to be
listed below as contributors.

Library's own tests
~~~~~~~~~~~~~~~~~~~

For simplicity, `Docker <https://docs.docker.com/install>`__ is required for running `the library's own tests <https://github.com/asyrjasalo/RESTinstance/tree/master/tests>`__. No other requirements are needed.

To spin up the environment and run the tests:

::

    ./test

To run them on Python 2.7:

::

    BUILD_ARGS="-f Dockerfile.python2" ./test

System under test
~~~~~~~~~~~~~~~~~

The test API is implemented by
`mounterest <https://github.com/asyrjasalo/mounterest>`__, which in turn
bases on `mountebank <https://www.mbtest.org>`__.

In the scope of library's tests, mounterest acts as a HTTP proxy to
`Typicode's live JSON server <jsonplaceholder.typicode.com>`__ and uses
mountebank's injections to enrich responses slightly, so that they
better match to this library's testing needs. Particularly, it allows
to test the library with non-safe HTTP methods (POST, PUT, PATCH,
DELETE) by mimicking their changes, instead of trying
to issue them on the live server. The changes are cleared between the test
runs.


Credits
-------

RESTinstance is licensed under `Apache License 2.0 <https://github.com/asyrjasalo/RESTinstance/blob/master/LICENSE>`__ and was originally written by Anssi Syrjäsalo.

It was presented at (the first) `RoboCon 2018 <https://robocon.io>`__.

We use the following Python excellence under the hood:

-  `GenSON <https://github.com/wolverdude/GenSON>`__, by Jon
   "wolverdude" Wolverton, for JSON Schema draft-04 creation
-  `Flex <https://github.com/pipermerriam/flex>`__, by Piper Merriam,
   for Swagger 2.0 validation
-  `jsonschema <https://github.com/Julian/jsonschema>`__, by Julian
   Berman, for JSON Schema draft-04 validation
-  `requests <https://github.com/requests/requests>`__, by Kenneth
   Reitz, for making HTTP requests

See `requirements.txt <https://github.com/asyrjasalo/RESTinstance/blob/master/requirements.txt>`__ for all the direct dependencies.
