*** Variables ***
${api_port}=                8273
${mb_port}=                 2525


*** Keywords ***
Reset state
    DELETE                  http://localhost:${api_port}/state

Create mountebank proxy
    &{response}=    POST    http://localhost:${mb_port}/imposters
    ...                     ${CURDIR}/imposter.json
    Set suite variable      ${MR_TOKEN}    ${response.body['port']}
    Set headers             { "X-Mounterest-Token": "${MR_TOKEN}" }
    Set headers             { "X-Mounterest-Property-ID": "id" }

Delete mountebank proxy
    DELETE                  http://localhost:${mb_port}/imposters/${MR_TOKEN}
