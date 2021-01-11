*** Settings ***
Library           REST    localhost:8273/
...               spec=${CURDIR}/swagger/spec_20.json

*** Test Cases ***
GET to existing
    GET    /users/1    allow_redirects=${None}

GET to non-existing
    GET    /users/404    allow_redirects=true

GET many
    GET    /users    allow_redirects=false

GET many with query "_limit"
    GET    /users?_limit=10    allow_redirects=${False}

GET many with invalid query
    GET    /users?_invalid=query    timeout=2.0

POST with invalid params
    POST    /users    { "name": "Alexander James Murphy" }

POST with valid params
    POST    /users    { "id": 100, "name": "Alexander James Murphy" }

POST with missing params
    POST    /users

PUT to non-existing
    PUT    /users/2043

PUT with invalid params
    PUT    /users/100    { "id": 1801 }

PUT with valid params
    PUT    /users/100    { "address": { "city": "Delta City" } }

PUT with missing params
    PUT    /users/100

PATCH to non-existing
    PATCH    /users/2043

PATCH with invalid params
    PATCH    /users/100    { "nickname": "murph" }

PATCH with valid params
    PATCH    /users/100    { "username": "murph" }

PATCH with missing params
    PATCH    /users/100

DELETE to non-existing
    DELETE    /users/2043

DELETE to existing
    DELETE    /users/100

DELETE to invalid, but with no validations
    DELETE    /invalid    validate=false
