*** Settings ***
Resource        resources/mounterest.robot
Suite teardown  Rest instances          ${OUTPUTDIR}/unicode_instances.json
Test setup      Reset state


*** Test Cases ***
POST and GET with unicode in payload
    POST        /users                  { "id": 13, "name": "Anssi Syrjäsalo" }
    String      request body name       Anssi Syrjäsalo
    String      response body name      "Anssi Syrjäsalo"
    GET         /users/13
    String      response body name      Anssi Syrjäsalo

PUT with unicode in payload
    PUT         /users/7                ${CURDIR}/payloads/unicode.json
    String      request body name       "❤❤❤"
    String      response body name      ❤❤❤

PATCH with unicode in payload
    PATCH       /users/9                { "name": "🤖🤖🤖" }
    String      response body name      🤖🤖🤖
    Output      file_path=${OUTPUTDIR}/unicode_instance.json
