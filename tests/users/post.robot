*** Settings ***
Library         REST                        localhost:8273
Test Setup      Generate random params

*** Keywords ***
Generate random params
    GET         http://localhost:8273/users/1
    ${schema}=  Object      schema response body
    Integer     response body id            minimum=11  maximum=20  skip=true
    String      response body name          "äääää!"             skip=true
    POST        http://localhost:8274       ${schema}   # POST JSON Schema
    &{fake}     GET         http://localhost:8274       # GET JSON from schema
    Set Test Variable       &{params}       &{fake.body}

*** Test Cases ***
Successful create
    GET         /users/99
    Integer     response status             404
    POST        /users                      ${params}
    Integer     response status             201
    GET         /users/${params.id}
    Integer     response body id            ${params.id}
    String      response body name          "äääää!"
    #Output      response body
