*** Settings ***
Library           OperatingSystem
Library           REST

*** Variables ***
${json_string}=    { "robotframework": "❤" }
&{json_dict}=     robotframework=🤖

*** Keywords ***
Clean Output file
    Remove File    ${OUTPUTDIR}/integer.txt

*** Test Cases ***
Output string
    Output    ${json_string}

Output dict
    Output    ${json_dict}

Output non-string Python value
    Output    ${1}    file_path=${OUTPUTDIR}/integer.txt
    Output    ${1.0}
    Output    ${True}
    Output    ${False}
    Output    ${None}

Output also_console boolean
    [Setup]    Clean Output file
    Output    ${json_dict}    file_path=${OUTPUTDIR}/integer.txt    also_console=${True}
    File Should Exist    ${OUTPUTDIR}/integer.txt
    [Teardown]    Clean Output file

Output also_console string
    [Setup]    Clean Output file
    Output    ${json_dict}    file_path=${OUTPUTDIR}/integer.txt    also_console=True
    File Should Exist    ${OUTPUTDIR}/integer.txt
    [Teardown]    Clean Output file

No output to console boolean
    [Setup]    Clean Output file
    Output    ${json_dict}    file_path=${OUTPUTDIR}/integer.txt    also_console=${False}
    File Should Exist    ${OUTPUTDIR}/integer.txt
    [Teardown]    Clean Output file

No output to console string
    [Setup]    Clean Output file
    Output    ${json_dict}    file_path=${OUTPUTDIR}/integer.txt    also_console=False
    File Should Exist    ${OUTPUTDIR}/integer.txt
    [Teardown]    Clean Output file

Output file content
    ${file}    Input    ${CURDIR}/payloads/unicode.json
    Output    ${file}

Output the last instance
    GET    https://jsonplaceholder.typicode.com/users/1
    Output

Output instance field
    GET    https://jsonplaceholder.typicode.com/users/1
    Output    response body name
    Output    response body id
