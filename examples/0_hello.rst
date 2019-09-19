We want You to join RESTinstance
================================

For who are we for?
-------------------

This tutorial assumes you already know the very basics of Robot Framework:

- test suites
- test cases
- setups and teardowns
- variables
- how to run tests

Neither RESTinstance, nor Robot Framework, assume having any programming skills,
but due to the technical nature of API testing, some HTTP must be known:

- What are the HTTP methods and request parameters (body, query)
- What is role of the response status and response body
- How to authenticate to APIs with request headers

The library bases its keywords on these terms because they are strongly rooted,
been used since the dawn of the Internet. Developers and sysadmins will already
feel at home with the termilogy, yet they don't have to learn a new language.

In addition, knowing the principles of REST is useful, library being designed
with RESTful APIs in mind. Though, we will also provide examples on testing APIs
in a stateful manner, e.g. several APIs must be called in a particular order.

As a note for developers, even though this library is programming language
agnostic (as well as HTTP, JSON and Robot Framework themselves), all the inputs
are accepted regardless whether being presented according to JSON or Python
type systems. In practice, test data can be of JSON ``object``s and ``array``s
or Python ``dict``s and ``list``s, respectively, and it is handled the same.


What we aim for?
----------------

Regarding tests, the library's main goal is to enable having them as short as
possible, only a few lines at max. We also strive for minimum number of keywords
in the library, to minimize the time spent searching the keyword documentation.

RESTinstance targets in acquiring as comprehensive test coverage as possible,
with as few keystrokes as possible. Keeping the tests short, having to remember
only a few keywords, it targets to be one of the most efficient JSON API testing
tools, and not being bound by GUIs.

Benefitting from Robot Framework and its ecosystem, one can extend the library
with user keywords, take the library into use in browser tests, for testing
parts that are fragile to test via UI, or combine both for more e2e like tests.


We got you covered.
-------------------

RESTinstance takes a strict view on types, seeing them as the absolute
minimum requirement and truth that must hold for reliably testing anything:
If an integer 1 would be interpret as a string, it would have unexpected
consequences as 1+1 would not equal 2 but "11".

In practice, if you assume wrong type for the property, the keyword immediately
raises an error, rather than implicitly tries to convert to more suitable type.

JSON types also have major role in JSON Schemas and Swagger/OpenAPI
specifications (due to both having the same origin): JSON Schema implements
its validation keywords per type (not to be confused with Robot Framework
keywords), providing all kinds of checks one would ever need when testing JSON.

Thus, RESTinstance bases all its validations on these JSON Schema validation
keywords, and them only, meaning that there is no other validation logic
implemented in the library itself. This is one of the key design decisions,
as implementing own validations would also increase the risk of having defects,
which could lead to the test library producing invalid test results at worst.

For larger JSON data sets, e.g. for validating thousands of JSON objects'
properties with a single query, the library supports JSONPath.
Even though more of an intermediate feature, than part of the essentials,
it also is a handy shortcut for accessing very deeply nested JSON properties.


Hello RESTinstance
------------------

You should have Robot Framework and RESTinstance installed at this point.
If not, see README.md in the repository root for the instructions.

We will use
`https://jsonplaceholder.typicode.com/users <https://jsonplaceholder.typicode.com/users>`__ as the system under test (SUT) for all the examples.


Taking the library into use:

.. code:: robotframework

    *** Settings ***
    Library       REST    https://jsonplaceholder.typicode.com

    *** Test cases ***
    This is soon to be the name of our test
      No operation



When using https and the endpoint not having a valid SSL certificate,
you must set ``ssl_verify`` to ``false``:

.. code:: robotframework

    *** Settings ***
    Library       REST    https://jsonplaceholder.typicode.com  ssl_verify=false

    *** Test cases ***
    For now, it is present to run this file with: robot 0_hello.rst
      No operation

For this API this makes no difference as a valid certificate is used for the URL.



If no protocol is given part of the URL, ``http://`` is assumed:

.. code:: robotframework

    *** Settings ***
    Library       REST    jsonplaceholder.typicode.com

    *** Test cases ***
    You can run `.rst` docs as if they were Robot Framework test suites
      No operation



Finishing this part, you should be familiar with:

- Basic concepts of Robot Framework
- HTTP terminology when it comes to request and response
- Taking RESTinstance into use

We continue by learning the HTTP keywords in the next part. See you there!
