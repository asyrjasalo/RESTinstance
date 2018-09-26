Request and response
====================

We are using `https://jsonplaceholder.typicode.com/users <https://jsonplaceholder.typicode.com/users>`__ as the system under test (SUT) for all the examples.


Sending GET request to an endpoint is easy as:

.. code:: robotframework

    *** Settings ***
    Library       REST      https://jsonplaceholder.typicode.com

    *** Test cases ***
    Get all users
      GET         /users



Let's GET only one user, and add ``Output`` to gain some more knowledge:

.. code:: robotframework

    *** Settings ***
    Library       REST      https://jsonplaceholder.typicode.com

    *** Test cases ***
    Get one user and output what we call an instance
      GET         /users/1
      Output

The output is what the library calls an instance. It is represented as JSON
itself, contains the details on what was the request and the response.

It also includes the automatically generated JSON Schema for the both,
optionally a Swagger/OpenAPI specification that both the request and
the response are valid against. More on schemas and specs later in the tutorial:
For now it is enough to know, that this kind of data is handled by the library.



There are no limitations in how many request we can send in a single test case.
Pay attention though how ``Output`` only outputs the last (user with id ``2``):

.. code:: robotframework

    *** Settings ***
    Library       REST      https://jsonplaceholder.typicode.com

    *** Test cases ***
    Get two users, notice how only the last instance is output
      GET         /users/1
      GET         /users/2
      Output

The library design is that most of its keywords only affect the last instance
(remember: the last request and response pair). We will soon learn that this is
the case with all the validations as well.

As the library scope is test suite, the previous instances are kept in memory
until the test suite execution has finished. We will later familiarize
ourselves on how to output all the created instances so far.



In this example, we limit the output to the response, which is enough
for knowing what was responded by the API endpoint:

.. code:: robotframework

    *** Settings ***
    Library       REST      https://jsonplaceholder.typicode.com

    *** Test cases ***
    Get one user, output the response
      GET         /users/1
      Output      response



Let's limit ``Output`` even further, to the response body. Also notice how it
can be written to a file instead of terminal, by using argument ``file_path``:

.. code:: robotframework

    *** Settings ***
    Library       REST          https://jsonplaceholder.typicode.com

    *** Test cases ***
    Get one user, write response body to file user_1.json
      GET         /users/1
      Output      response body   file_path=${CURDIR}/user_1.json

Robot Framework automatic variable ``${CURDIR}`` points to the directory
where the test suite (this file) is in.



So, what the ``response body`` part for ``Output`` essentially is,
is the path in the JSON. Knowing this, let's output ``address`` of our user:

.. code:: robotframework

    *** Settings ***
    Library       REST    # note that we can have URL per request as well

    *** Test cases ***
    Get one user, output the address of the first user
      GET         https://jsonplaceholder.typicode.com/users/1
      Output      response body address

Keyword ``Output`` may become the most valuable keyword when writing these tests:
It is usually faster to debug this way than opening ``log.html`` and browsing
to the correct keyword.



In addition to ``Output``ting request and response properties, the keyword
can output all kinds of values and variables:

.. code:: robotframework

    *** Settings ***
    Library       REST

    *** Variables ***
    ${json}=      {"foo": "bar" }   # JSON object, represented as Python str
    &{dict}=      foo=bar           # Python dict, corresponds to JSON object
    ${array}=     ["foo", "bar"]    # JSON array, represented as Python str
    @{list}=      foo   bar         # Python list, corresponds to JSON array

    *** Test cases ***
    Demonstrate different uses of Output keyword
      Output      "Use double quotes to distinct JSON string from a property"
      Output      { "key": "value" }
      Output      ${json}
      Output      ${dict}
      Output      ${array}
      Output      ${list}

Comments shed some light on how the test data is handled internally by the
library - just in case you were wondering, not crucial in terms of testing.



So far we have been only using ``GET``, so let's throw in the rest of
the HTTP keywords. Also, now that we know variables, we can use them for storing
test data. Besides variables, we can load test data from files:

.. code:: robotframework

    *** Settings ***
    Library         REST        https://jsonplaceholder.typicode.com/users
    Documentation   To find more information on different HTTP methods, check
    ...             https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
    ...
    ...             P.S.: Definitely a must-read if developing RESTful APIs!

    *** Variables ***
    ${new_props}=   { "pockets": "", "money": 0.02 }

    *** Test cases ***
    GET all the existing users
      GET           /users

    GET the existing user
      GET           /users/1

    POST to create a new user
      POST          /users      ${CURDIR}/user_1.json

    PUT to update the existing user - might allow creating one too
      PUT           /users/1    ${new_props}

    PATCH to update a single property of the existing user
      PATCH         /users/1    { "name": "Gil Alexander" }

    DELETE an existing user
      DELETE        /users/1

    # The next two methods are implemented by web servers mostly to give
    # info to clients. They should not do anything related to the data.

    HEAD is identical to GET, but has nothing in response body
      HEAD          /users/1

    OPTIONS is used to gain info on the allowed communication options
      OPTIONS       /users/1

This is how the tests are intented to be written for RESTful APIs:
One request per test case. This leads to clean-looking tests, soon when we start
actually testing the responses - here we are just sending a couple of requests.



Two more things in this part, both regarding HTTP keywords' optional arguments:

1. You can define an explicit ``timeout`` per requests. This is useful,
if some particular request is prone to hang, causing tests to hang as well.
If the timeout exceeds, the keyword will fail (thus this is our first test!).

If you notice the test execution hanging, or taking too long and you want to
fail the execution due to it, check using Robot Framework's own timeouts.

2. By default, one or more redirects will happen automatically for keywords
``GET``, ``OPTIONS``, ``POST``, ``PUT``, ``PATCH`` and ``DELETE``,
if the response status code indicates so (3xx, e.g. 301, Moved Permanently).
To prevent any redirection, set ``allow_redirects`` to ``false``.

For ``HEAD``, no redirects will happen unless explictly allowed by setting
``allow_redirects`` to ``true``.

.. code:: robotframework

    *** Settings ***
    Library         REST        https://jsonplaceholder.typicode.com/users

    *** Test cases ***
    GET all the existing users, timeout if takes more than a second
      GET           /users      timeout=1.0

    GET the existing user, prevent any redirects
      GET           /users/1    allow_redirects=false

    HEAD to get headers, allow redirects that normally would not happen
      HEAD          /users/1    allow_redirects=true



Finishing this part, you should:

- Be able to use keyword ``Output`` for debugging purposes
- Know that instance is request and response, their schemas, optionally a spec
- Know that the most keywords of RESTinstance only affect the last instance
- Be able to test data from variables or files
- Be familiar with all the HTTP keywords

We will learn authentication and HTTP headers in the next part. See you there!
