*** Settings ***
Library             Collections
Library             FakerLibrary        seed=10                 locale=${locale}
Library             REST                http://localhost:2525   # mountebank
Suite setup         Create /users in mountebank
#Suite teardown      Delete /users in mountebank

*** Variables ***
${locale}=          en_US
${api_port}=        8080
${resource}=        users
${how_many}=        10

*** Keywords ***
Create /users in mountebank
    &{imposter}=    Input               { "name": "test doubles for /${resource}", "protocol": "http", "port": ${api_port}, "defaultResponse": { "statusCode": 400, "body": { "error": "bad request" }, "headers": { "Content-Type": "application/json" }}, "stubs": [] }

    @{users}=       Create List

    # Get to id
    :FOR  ${id}  IN RANGE  1  ${how_many}+1
    \   &{user}=                        Create Dictionary

    \   ${user.id}=                     Set Variable            ${id}
    \   ${user.uuid}=                   Uuid4
    \   ${user.name}=                   Name
    \   ${user.email}=                  Email
    \   ${user.phone}=                  Phonenumber

    \   ${user.address}=                Create Dictionary
    \   ${user.address.street}=         Street Address
    \   ${user.address.postalcode}=     Postcode
    \   ${user.address.city}=           City

    \   ${user.address.geo}=            Create Dictionary
    \   ${lat}=                         Latitude
    \   ${lng}=                         Longitude
    \   ${user.address.geo.latitude}=   Convert to number       ${lat}
    \   ${user.address.geo.longitude}=  Convert to number       ${lng}

    \   ${user.urls}=                   Create List
    \   ${url1}=                        URI
    \   Append to list                  ${user.urls}            ${url1}
    \   ${url2}=                        URI
    \   Append to list                  ${user.urls}            ${url2}

    \   ${user.organizationId}=         Input                   null
    \   ${user.active}=                 FakerLibrary.Boolean    # overlapping kw
    \   ${user.registeredAt}=           ISO8601
    \   Append to list                  ${users}                ${user}

    \   ${body}=            Evaluate    json.dumps(${user})     modules=json
    \   ${stub}=            Input       { "responses": [ { "is": { "statusCode": 200, "body": ${body} } } ], "predicates": [ { "matches": { "path": "^/${resource}/${id}/?$" }}] }
    \   Append to list                  ${imposter.stubs}       ${stub}

    # Get to all
    ${body}=                Evaluate    json.dumps(${users})    modules=json
    ${stub}=                Input       { "responses": [ { "is": { "statusCode": 200, "body": ${body} } } ], "predicates": [ { "matches": { "path": "^/${resource}/?$" }}] }
    Append to list                      ${imposter.stubs}       ${stub}

    # Default response
    ${default_stub}=        Input       { "responses": [ { "is": { "statusCode": 404, "body": { "error": "not found" }}} ] }
    Append to list  ${imposter.stubs}   ${default_stub}

    # Create in mountebank
    POST                    /imposters  ${imposter}

Delete /users in mountebank
    DELETE                  /imposters/${api_port}
