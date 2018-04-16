*** Settings ***
Library         REST              https://jsonplaceholder.typicode.com


*** Test Cases ***
GET an existing user
    GET         /users/1
    Integer     $.id                    1
    String      $.name                  Leanne Graham

GET existing users
    GET         /users?_limit=1
    Array       $
    Object      $[0]
    Integer     $[0].id                 1
