
    ██████╗ ███████╗███████╗████████╗
    ██╔══██╗██╔════╝██╔════╝╚══██╔══╝
    ██████╔╝█████╗  ███████╗   ██║
    ██╔══██╗██╔══╝  ╚════██║   ██║
    ██║  ██║███████╗███████║   ██║
    ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝

    ██╗███╗   ██╗███████╗████████╗ █████╗ ███╗   ██╗ ██████╗███████╗
    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║██╔════╝██╔════╝
    ██║██╔██╗ ██║███████╗   ██║   ███████║██╔██╗ ██║██║     █████╗
    ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║╚██╗██║██║     ██╔══╝
    ██║██║ ╚████║███████║   ██║   ██║  ██║██║ ╚████║╚██████╗███████╗
    ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝

    Robot Framework test library for (RESTful) JSON APIs


## Why?

1. **RESTinstance bases from Robot Framework's language-agnostic, keyword-driven
syntax** for API tests. As with Robot Framework, using it is not tied
to any programming language nor development framework.
RESTinstance rather keeps things simple and the language humane, also for
the testers without programming knowledge. It builts on long-term
technologies, that have already established communities, such as HTTP,
JSON (Schema), OpenAPI and Robot Framework.

2. **It validates JSON using JSON Schema, guiding you to write API tests
basing on constraints** (e.g. "response body property email must be a valid
email") rather than on specific values (e.g. response body property email
is "foo@bar.com"). This reduces test maintenance when values returned by
the API are prone to change. Although validations do not require values,
you can still use them whenever they make sense (e.g. GET response body
from one endpoint, then POST some of its values to another endpoint).

3. **It generates JSON Schema for requests and responses automatically,
and the schema gets more accurate by your tests.**
This schema can be used as a documentation or a contract between
different teams, or specialities (e.g. testers, developers), to agree on
what kind of data the API handles. Additionally, you can mark validations
to be skipped, and rather use the tests to define how the API should work,
if the API does not exist yet - then the produced schema also acts as a design.
The schema can be further used as a base for writing an OpenAPI specification,
which RESTinstance can also test against (spec version 2.0, the support for 3.0
and generating also an OpenAPI spec automatically is planned).


## Installation

### Python 3 (only):

    pip install --upgrade RESTinstance

### Using Docker

If you have Docker available, prefer
[rfdocker](https://github.com/asyrjasalo/rfdocker).

To take this library into use, add `RESTinstance` to `requirements.txt`
and comment out the `requirements.txt` installation line in `Dockerfile`.
Then run your `./tests` with `./rfdocker`.


## Usage

See [keyword documentation](https://github.com/asyrjasalo/RESTinstance/tree/master/docs/REST.html) for all the keywords.

RESTinstance targets to cover (at least) three kind of API tests:

1. **Testing for JSON types and formats using JSON Schema validations.**
For examples, see `tests/validations.robot`.

2. **Flow-driven API tests, i.e. multiple APIs are called for the end result.**
For examples, see `tests/methods.robot`.

3. **Testing API requests and responses against a schema or a specification.**
For examples testing against JSON schemas, see `tests/schema.robot`
and for testing against Swagger 2.0 specification, see `tests/spec.robot`.


## Development

The issues and feature requests are tracked in GitHub issue tracker.

We kindly do take pull requests. Please mention if you do not want your
name listed in contributors.

### Library's own tests

Docker is mandatory for running the library's own tests.

To start the test API and run the tests:

    ./test

### The test API

This system under test is implemented by
[mounterest](https://github.com/asyrjasalo/mounterest),
which in turn bases on [mountebank](http://www.mbtest.org).

In the scope of this library's tests, mounterest acts as a HTTP proxy to
[Typicode's live JSON server](jsonplaceholder.typicode.com) and uses
mountebank's injections to enrich the responses from there slightly,
so that they better match to this library's testing needs.

Particularly, the injectors bundled in mounterest allow us to test
the library also with non-safe HTTP methods (POST, PUT, PATCH, DELETE).
Otherwise they would have no effect, as the live server is read-only.

These injectors share a state and intercept non-safe HTTP requests,
mimicking their changes in the state only, instead of trying to do
them on the live-server. This state is cleared between the test runs.

You may benefit from mounterest for your own purposes, if you are
e.g. lacking a test environment where you can make changes.
The tool is under active development but outside the scope of this library.
See [GitHub repository](https://github.com/asyrjasalo/mounterest) for more.


## Credits

RESTinstance is licensed under Apache License 2.0.

RESTinstance was originally written by Anssi Syrjäsalo, and was initially
presented at [RoboCon 2018](https://robocon.io), in Helsinki, Finland.

RESTinstance 1.0.0 was released at 2018-03-01.

### Python community

In addition to Robot Framework, RESTinstance uses the following (excellent!)
Python tools under the hood:

- [GenSON](https://github.com/wolverdude/GenSON), by Jon "wolverdude" Wolverton,
for JSON Schema generation
- [Flex](https://github.com/pipermerriam/flex), by Piper Merriam,
for Swagger 2.0 validation
- [jsonschema](https://github.com/Julian/jsonschema), by Julian Berman,
for JSON Schema draft-04 validation
- [requests](https://github.com/requests/requests), by Kenneth Reitz,
for Python HTTP requests

See `requirements.txt` for list of all the (direct) dependencies.