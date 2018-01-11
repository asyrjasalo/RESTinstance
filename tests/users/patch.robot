*** Settings ***
Library         REST                    localhost:8273
...             schema={ "response": { "status": { "not": { "enum": [200] }} } }

*** Test Cases ***
Failed PATCH
    PATCH       /users/1                { "notExist": 7 }
    Integer     response status         400
    String      response body error     pattern="^Cannot change property.*$"
