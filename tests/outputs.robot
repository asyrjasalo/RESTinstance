*** Settings ***
Library         REST                    https://jsonplaceholder.typicode.com


*** Test cases ***
Responding JSON object
    GET         /users/1
    String      response body email     format=email
    Output      schema response body    ${CURDIR}/outputs/body_object.json

Responding JSON array
    GET         /users
    String      response body 0 name    Leanne Graham   minLength=3
    String      response body 0 name    Ervin Howell    Leanne Graham
    Output      schema response body    ${CURDIR}/outputs/body_array.json

Method with query parameters
    GET         /users?_limit=10
    Object      request query
    Array       request query _limit    [ "10" ]
    String      response body 0 name    Leanne Graham   minLength=3
    String      response body 1 name    "Ervin Howell"  pattern="[A-Za-z]+"
    Output      schema                  ${CURDIR}/outputs/request_query.json

Method with body parameters
    POST        /users                  { "id": 11, "name": "Gil Alexander" }
    Integer     request body id         11
    String      request body name       Gil Alexander
    Output      schema                  ${CURDIR}/outputs/request_body.json
