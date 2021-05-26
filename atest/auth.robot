*** Settings ***
Library           REST    

*** Variables ***
${baseurl} =      https://postman-echo.com
${user} =         postman
${password}=      password

*** Test Cases ***
GET Basic Auth
    ${url}  Set Variable  ${baseurl}/basic-auth

    Set Client Authentication  basic  ${user}  ${password}
    GET        ${url}
    Integer    response status    200
 
    Set Client Authentication  digest  ${user}  ${password}
    Run Keyword And Expect Error  KeyError: 'content-type'  
    ...        GET        ${url}
    Integer    response status    401

    Set Client Authentication  ${NONE}
    Run Keyword And Expect Error  KeyError: 'content-type'  
    ...        GET        ${url}
    Integer    response status    401

GET Digest Auth
    ${url}  Set Variable  ${baseurl}/digest-auth
 
    Set Client Authentication  digest  ${user}  ${password}
    GET        ${url}
    Integer    response status    200

    Set Client Authentication  basic  ${user}  ${password}
    Run Keyword And Expect Error  KeyError: 'content-type'  
    ...        GET        ${url}
    Integer    response status    401

    Set Client Authentication  ${NONE}
    Run Keyword And Expect Error  KeyError: 'content-type'  
    ...        GET        ${url}
    Integer    response status    401
