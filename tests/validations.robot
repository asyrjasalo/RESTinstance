*** Settings ***
Library         REST       localhost:8273   schema={ "exampled": false }
Suite setup     DELETE     /invalidate
Test setup      Set expectations


*** Keywords ***
Set expectations
    Expect response         { "status": { "enum": [200, 201, 204, 400] } }
    Expect response         { "seconds": { "maximum": 1.5 } }


*** Test Cases ***
GET existing user
    GET         /users/1
    String      response body username      minLength=4
    String      response body email         format=email
    String      response body address geo lat   "-37.3159"

GET many users
    GET         https://jsonplaceholder.typicode.com/users?_limit=5
    Array       response body               maxItems=5

POST with valid params
    POST        /users                      { "id": 15, "name": "Gil Alexander" }
    Object      response body               required=["id", "name"]

PUT with invalid params
    PUT         /users/5                    { "id": 1969 }
    String      response body error         pattern=read-only

PUT with valid params
    PUT         /users/5                    { "website": "https://robocon.io" }
    String      response body website       format=uri

PATCH with invalid params
    PATCH       /users/8                    { "id": "1984" }
    String      response body error         pattern="not allowed$"

DELETE existing
    DELETE      /users/6

