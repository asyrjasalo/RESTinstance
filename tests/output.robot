*** Settings ***
Library                 REST


*** Variables ***
${json_string}=         { "robotframework": "🤖" }
&{json_dict}=           robotframework=🤖


*** Test Cases ***
Log JSON to console with string input
    Output    ${json_string}
    Output    { "robotframework": "❤" }

Log JSON to console with dict input
    Output    ${json_dict}

Log JSON to console with file input
    ${json}=  Input     ${CURDIR}/payloads/unicode.json
    Output    ${json}

Log JSON to console with instance field input
    GET       https://jsonplaceholder.typicode.com/users/1
    Output    response body name

Log JSON to console with invalid input
    GET       https://jsonplaceholder.typicode.com/users/1
    Run Keyword And Expect Error
    ...       This is not a string or dict:\n1
    ...       Output    ${1}
