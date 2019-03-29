*** Settings ***
Library         REST                    localhost:8273/
Test setup      DELETE                  http://localhost:8273/state


*** Test cases ***
Responding JSON object
    GET         /users/1
    String      response body email     format=email
    Output schema   response body       ${CURDIR}/schemagen/body_object.json
    ...                                 sort_keys=true

Responding JSON array
    GET         /users
    String      response body 0 name    Leanne Graham   minLength=3
    String      response body 0 name    Ervin Howell    Leanne Graham
    Output schema   response body       ${CURDIR}/schemagen/body_array.json
    ...                                 sort_keys=true

Method with query parameters
    GET         /users?_limit=10
    Object      request query
    String      request query _limit    10
    GET         /users?_limit=10        { "_limit": "5" }
    String      request query _limit    5
    String      response body 0 name    Leanne Graham   minLength=3
    String      response body 1 name    "Ervin Howell"  pattern="[A-Za-z]+"
    Output schema               file_path=${CURDIR}/schemagen/request_query.json
    ...                                 sort_keys=true

Method with body parameters
    POST        /users                  { "id": 11, "name": "Gil Alexander" }
    Integer     request body id         11
    String      request body name       Gil Alexander
    Output schema               file_path=${CURDIR}/schemagen/request_body.json
    ...                                 sort_keys=true

# GenSON 0.2.3
With 'type' as payload property
    PUT         /users/7                    { "type": "not_schema_kw" }
    String      response body type          not_schema_kw

With 'items' as payload property
    PUT         /users/7                    { "items": "not_schema_kw" }
    String      response body items         not_schema_kw

With 'properties' as payload property
    PUT         /users/7                    { "properties": "not_schema_kw" }
    String      response body properties    not_schema_kw

With 'required' as payload property
    PUT         /users/7                    { "required": "not_schema_kw" }
    String      response body required      not_schema_kw

# GenSON 1.0.1
With '$schema' as payload property
    PUT         /users/7                    { "$schema": "not_schema_kw" }
    String      response body $schema       not_schema_kw

With 'patternProperties' as payload property
    PUT         /users/7                { "patternProperties": "not_schema_kw" }
    String      response body patternProperties      not_schema_kw

With 'anyOf' as payload property
    PUT         /users/7                    { "anyOf": "not_schema_kw" }
    String      response body anyOf         not_schema_kw
