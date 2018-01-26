*** Settings ***
Library         REST                http://mounterest:${api_port}

*** Variables ***
${api_port}=                        8273

*** Keywords ***
Reset state
    DELETE            http://mounterest:${api_port}/state     spec=null
