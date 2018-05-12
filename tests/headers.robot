*** Settings ***
Library       REST  https://httpbin.org

*** Variables ***
${oauth_token}    0b79bab50daca910b000d4f1a2b675d604257e42
${base64_creds}   base64EncodedUsernameAndPassword
&{basic_auth}     Authorization=Basic ${base64_creds}   # no quotes here!

*** Test Cases ***
From a JSON string
  [Setup]     Set headers   { "Authorization": "Bearer ${oauth_token}" }
  Get         /get
#  [Teardown]  Output        response body headers Authorization

From a JSON file
  [Setup]     Set headers   ${CURDIR}/headers.json
  Get         /get
#  [Teardown]  Output        $.headers.Authorization

From a Python dictionary
  [Setup]     Set headers   ${basic_auth}
  Get         /get
#  [Teardown]  Output        $..Authorization
