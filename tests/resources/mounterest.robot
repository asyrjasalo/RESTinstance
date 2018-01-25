*** Settings ***
Library         REST                http://localhost:${api_port}

*** Variables ***
${api_port}=                        8273

*** Keywords ***
Reset state
    Set headers                     { "Host": "jsonplaceholder.typicode.com" }
