*** Settings ***
Library         REST                            localhost:8273

*** Test Cases ***
Successful update
    GET         /users/1
    Null        response body organizationId
    PUT         /users/1                        { "organizationId": 7 }
    Integer     response status                 200
    GET         /users/1
    Integer     response body organizationId    7
