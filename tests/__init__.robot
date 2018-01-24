*** Settings ***
Library         REST       http://localhost:2525
Library         Collections
Suite setup     Create proxy to jsonplaceholder.typicode.com
Suite teardown  Invalidate state in mounterest

*** Variables ***
${api_port}=                8080

*** Keywords ***
Create proxy to jsonplaceholder.typicode.com
    &{imposter}=  Input     { "name": "proxy to live jsonserver", "protocol": "http", "port": ${api_port}, "stubs": [] }
    ${proxy}=     Input     ${CURDIR}/proxy.json
    Append to list          ${imposter.stubs}   ${proxy}
    POST                    /imposters          ${imposter}

Invalidate state in mounterest
    DELETE                  http://localhost:8273/state
