*** Settings ***
Library         REST                            localhost:8273  ssl_verify=false
Suite setup     Set headers and assume schema   ${CURDIR}/json/headers.json
Suite teardown  Rest instances                  ${OUTPUTDIR}/instances.json

*** Keywords ***
Set headers and assume schema
    [Arguments]         ${headers}
    Set headers         ${headers}
    Expect response     ${CURDIR}/schemas/response_status.json

*** Test Cases ***
Get found
    GET             /users/1                    timeout=3.0
    Boolean         response body active        true
    String          response body strActive     true
    Integer         response body id            1
    Number          response body address geo latitude    ${-74.490087}
    &{body}         Object                      response body
    @{enum_id}=     Input                       [1, 3, "4"]
    Integer         response body id            @{enum_id}
    String          response body name          minLength=2
    Output                                      file_path=results/get.json

Get not found
    GET             /users/100
    Integer         response status             404
