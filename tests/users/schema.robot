*** Settings ***
Library         REST        localhost:8273
Test teardown   Clear expectations

*** Test Cases ***
Request and response conforms the schema
    Expect request          ${CURDIR}/schemas/request.json
    Expect response         ${CURDIR}/schemas/response.json
    :FOR  ${id}  IN RANGE  3  11
    \   GET     /users/${id}
