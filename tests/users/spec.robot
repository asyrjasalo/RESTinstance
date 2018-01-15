*** Settings ***
Library         REST        localhost:8273     spec=${CURDIR}/openapi/users.json

*** Test Cases ***
Get one
    :FOR  ${id}  IN RANGE  1  11
    \   GET     /users/${id}

Get many
    GET         /users/
