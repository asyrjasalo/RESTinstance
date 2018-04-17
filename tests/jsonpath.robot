*** Settings ***
Library         REST                https://jsonplaceholder.typicode.com


*** Test Cases ***
Query with JSONPath from response body object
    GET         /users/1
    Integer     $.id                1
    Integer     $[id]               1
    String      $.name              Leanne Graham
    String      $..lat              -37.3159
    String      $.company.name      Romaguera-Crona

Query with JSONPath from response body array
    GET         /users?_limit=5
    Array       $
    Object      $[0]
    Integer     $[0].id             1
    Integer     $[4].id             5
    Integer     $[*].id             1   2   3   4   5
