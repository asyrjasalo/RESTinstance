*** Settings ***
Library           REST    localhost:8273/
Suite Setup       DELETE    http://localhost:8273/state
Suite Teardown    Rest instances
Test Setup        Set expectations
Test Teardown     Clear expectations

*** Keywords ***
Set expectations
    Expect request    ${CURDIR}/schemas/valid/request.yaml
    Expect response    ${CURDIR}/schemas/valid/response.json

*** Test Cases ***
GET to existing
    GET    /users/1

GET to non-existing
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    GET    /users/404

GET many
    GET    /users

GET many with query "_limit"
    GET    /users?_limit=10

GET many with invalid query
    GET    /users?_invalid=query

POST with invalid params
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    POST    /users    { "name": "Alexander James Murphy" }

POST with valid params
    &{response}=    GET    /users/1
    &{body}    Input    ${response.body}
    ${body.id}=    Input    50
    POST    /users    ${body}

POST with missing params
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    POST    /users

PUT to non-existing
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    PUT    /users/2043

PUT with invalid params
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    PUT    /users/50    { "id": 1801 }

PUT with valid params
    PUT    /users/2    { "address": { "city": "Delta City" } }

PUT with missing params
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    PUT    /users/2

PATCH to non-existing
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    PATCH    /users/2043

PATCH with invalid params
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    PATCH    /users/2    { "nickname": "murph" }

PATCH with valid params
    PATCH    /users/2    { "username": "murph" }

PATCH with missing params
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    PATCH    /users/2

DELETE to non-existing
    [Setup]    Expect response    ${CURDIR}/schemas/invalid/response.json
    DELETE    /users/2043

DELETE to existing
    DELETE    /users/10

DELETE to invalid, but with no validations
    DELETE    /invalid    validate=${False}

DELETE with body
    DELETE      /users/1/posts        {"id": 1345}
