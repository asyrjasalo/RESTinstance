*** Settings ***
Library         REST                      localhost:8273

*** Test Cases ***
Successful delete
    GET         /users/2
    Object      response body
    Integer     response status           200
    DELETE      /users/2
    Integer     response status           204
    String      response body             ""
    GET         /users/2
    Integer     response status           not={ "enum": [200] }
    Object      response body             { "error": "Not found" }
