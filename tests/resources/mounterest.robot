*** Settings ***
Library         REST                http://mounterest:${api_port}

*** Variables ***
${api_port}=                          %{MR_PORT}
${mb_port}=                           %{MB_PORT}

*** Keywords ***
Reset state
    DELETE            http://mounterest:${api_port}/state     spec=null
