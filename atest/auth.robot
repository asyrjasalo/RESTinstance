*** Settings ***
Library           REST

*** Variables ***
${baseurl} =      https://postman-echo.com
${user} =         postman
${password}=      password

*** Test Cases ***
GET Basic Auth
    ${url}    Set Variable    ${baseurl}/basic-auth
    Set Client Authentication    basic    ${user}    ${password}
    GET    ${url}
    Integer    response status    200
    Set Client Authentication    digest    ${user}    ${password}
    GET    ${url}
    Integer    response status    401
    Set Client Authentication    ${NONE}
    GET    ${url}
    Integer    response status    401

GET Digest Auth
    ${url}    Set Variable    ${baseurl}/digest-auth
    Set Client Authentication    digest    ${user}    ${password}
    GET    ${url}
    Integer    response status    200
    Set Client Authentication    basic    ${user}    ${password}
    GET    ${url}
    Integer    response status    401
    Set Client Authentication    ${NONE}
    GET    ${url}
    Integer    response status    401

Set Auth Invalid Args
    ${error}    Set Variable    TypeError: Argument "auth_type" must be \${NONE}, basic, digest or proxy.
    Run Keyword And Expect Error    ${error}
    ...    Set Client Authentication    none    ${user}    ${password}
    Run Keyword And Expect Error    ${error}
    ...    Set Client Authentication    doge    ${user}    ${password}
    Run Keyword And Expect Error    ${error}
    ...    Set Client Authentication    ${1}    ${user}    ${password}
