*** Settings ***
Library           REST    schema={ "examples": null }
Suite Setup       Set expectations
Test Setup        DELETE    http://localhost:8273/state

*** Variables ***
${api_url}=       http://localhost:8273

*** Keywords ***
Set expectations
    Expect response    { "status": { "enum": [200, 201, 204, 400] } }
    Expect response    { "seconds": { "maximum": 1.5 } }

*** Test Cases ***
GET existing user
    GET    ${api_url}/users/1
    String    response body username    minLength=4
    String    response body email    format=email
    String    response body address geo lat    "-37.3159"

GET many users
    GET    ${api_url}/users?_limit=5
    Array    response body    maxItems=5

Verify many things
    [Tags]    issue-73
    GET    ${api_url}/users?_limit=3
    Integer    response body 0 id    1
    String    response body 0 name    Leanne Graham
    Array    response body    skip=true

POST with valid params
    POST    ${api_url}/users    { "id": 15, "name": "Gil Alexander" }
    Object    response body    required=["id", "name"]

PUT with invalid params
    PUT    ${api_url}/users/5    { "id": 1969 }
    String    response body error    pattern=read-only

PUT with valid params
    PUT    ${api_url}/users/5    { "website": "https://robocon.io" }
    String    response body website    format=uri

PATCH with invalid params
    PATCH    ${api_url}/users/8    { "id": "1984" }
    String    response body error    pattern="not allowed$"

DELETE existing
    DELETE    ${api_url}/users/6
