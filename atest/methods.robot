*** Settings ***
Library           REST    localhost:8273/
Test Setup        DELETE    http://localhost:8273/state

*** Variables ***
&{invalid}=       name=John Galt
${valid}=         { "name": "Julie Langford" }

*** Test Cases ***
GET existing user
    GET    users/1
    Integer    response status    200
    Integer    response body id    1
    String    response body name    Leanne Graham
    String    response reason    OK

GET non-existing user
    GET    /users/1969
    Integer    response status    404
    String    response body error    Not found

GET many users
    GET    https://jsonplaceholder.typicode.com/users?_limit=3    timeout=1.5
    Integer    response body 2 id    3
    GET    http://jsonplaceholder.typicode.com/users    { "_limit": 3 }
    Array    response body    ${CURDIR}/responses/limit_3.json

POST with invalid params
    POST    /users    ${invalid}
    Integer    response status    400
    String    response body error    No property 'id' given

POST with valid params
    POST    /users    { "id": 11, "name": "Gil Alexander" }
    Integer    response status    201

PUT with valid params
    PUT    /users/2    { "isCoding": true }
    Boolean    response body isCoding    true
    PUT    /users/2    { "sleep": null }
    Null    response body sleep
    PUT    /users/2    { "pockets": "", "money": 0.02 }
    String    response body pockets    ${EMPTY}
    String    response body pockets    ""
    Number    response body money    0.02
    Missing    response body moving

PATCH with valid params
    GET    "/users/3"    # quotes are optional
    String    response body name    Clementine Bauch
    PATCH    /users/3    ${valid}
    String    response body name    Julie Langford

DELETE existing
    DELETE    /users/9
    Integer    response status    200    204
    GET    /users/9
    Number    response status    404
