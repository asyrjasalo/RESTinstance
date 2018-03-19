*** Settings ***
Resource        resources/mounterest.robot
Test setup      Reset state
#Test teardown   Output  schema response body


*** Test Cases ***
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
