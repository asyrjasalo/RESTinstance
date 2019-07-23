*** Settings ***
Library             REST


*** Variables ***
${json_string}=     { "robotframework": "❤" }
&{json_dict}=       robotframework=🤖


*** Test Cases ***
Output string
    Output          ${json_string}

Output dict
    Output          ${json_dict}

Output non-string Python value
    Output          ${1}        file_path=${OUTPUTDIR}/integer.txt
    Output          ${1.0}
    Output          ${True}
    Output          ${False}
    Output          ${None}

Output file content
    ${file}  Input  ${CURDIR}/payloads/unicode.json
    Output          ${file}

Output the last instance
    GET             https://jsonplaceholder.typicode.com/users/1
    Output

Output instance field
    GET             https://jsonplaceholder.typicode.com/users/1
    Output          response body name
    Output          response body id
