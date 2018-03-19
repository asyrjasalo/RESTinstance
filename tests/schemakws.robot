*** Settings ***
Resource        resources/mounterest.robot
Test setup      Reset state
#Test teardown   Output  schema response body


*** Test Cases ***
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
