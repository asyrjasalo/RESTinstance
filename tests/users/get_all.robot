*** Settings ***
Library         REST                      localhost:8273

*** Test Cases ***
Get all
    GET         users
    Integer     response status           200
    Array       response body             maxItems=10   items={ "type": "object", "properties": { "email": { "type": "string" }}}
    Boolean     response body 0 active
    Output      schema                    file_path=results/get_all_schema.json

Get with query params
    GET         http://jsonplaceholder.typicode.com/users?_start\=3   { "_end": 5 }
    Array       response body             minItems=2  maxItems=2
