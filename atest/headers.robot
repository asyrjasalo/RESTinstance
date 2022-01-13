*** Settings ***
Library           REST    https://httpbin.org

*** Variables ***
${oauth_token}    0b79bab50daca910b000d4f1a2b675d604257e42
${base64_creds}    base64EncodedUsernameAndPassword
&{basic_auth}     Authorization=Basic ${base64_creds}    # no quotes here!

*** Test Cases ***
From a JSON string
    [Setup]    Set headers    { "Authorization": "Bearer ${oauth_token}" }
    Get    /get

From a JSON file
    [Setup]    Set headers    ${CURDIR}/headers.json
    Get    /get

From a Python dictionary
    [Setup]    Set headers    ${basic_auth}
    Get    /get

Per request from JSON string
    Get    /get    headers={ "Authorization": "Bearer ${oauth_token}" }
    String    request headers Authorization    Bearer ${oauth_token}

Per request from a JSON file
    Get    /get    headers=${CURDIR}/headers.json
    String    request headers Authorization    Bearer ${oauth_token}

Per request from a Python Dictionary
    Get    /get    headers=${basic_auth}
    String    request headers Authorization    Basic ${base64_creds}

Inline Get Headers Should Not Persist
    Get    /get    headers={"Some header": "Value"}
    ${headers1}=    String    request headers    skip=true
    Get    /get
    ${headers2}=    String    request headers    skip=true
    Should Not Be Equal    ${headers1}    ${headers2}

Inline Post Headers Should Not Persist
    Post    /post    headers={"Some header": "Value"}
    ${headers1}=    String    request headers    skip=true
    Post    /post
    ${headers2}=    String    request headers    skip=true
    Should Not Be Equal    ${headers1}    ${headers2}

Inline Put Headers Should Not Persist
    Put    /put    headers={"Some header": "Value"}
    ${headers1}=    String    request headers    skip=true
    Put    /put
    ${headers2}=    String    request headers    skip=true
    Should Not Be Equal    ${headers1}    ${headers2}

Inline Patch Headers Should Not Persist
    Patch    /pacth    headers={"Some header": "Value"}
    ${headers1}=    String    request headers    skip=true
    Patch    /patch
    ${headers2}=    String    request headers    skip=true
    Should Not Be Equal    ${headers1}    ${headers2}

Inline Delete Headers Should Not Persist
    Delete    /delete    headers={"Some header": "Value"}
    ${headers1}=    String    request headers    skip=true
    Delete    /delete
    ${headers2}=    String    request headers    skip=true
    Should Not Be Equal    ${headers1}    ${headers2}
