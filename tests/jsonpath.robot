*** Settings ***
Library         REST                    https://jsonplaceholder.typicode.com


*** Test Cases ***
JSONPath query from object
    GET         /users/1
    Integer     $.id                    1
    Integer     $[id]                   1
    Integer     $."id"                  1
    String      $.name                  Leanne Graham
    String      $.'name'                 Leanne Graham
    String      $..lat                  -37.3159
    String      $.company.name          Romaguera-Crona
    String      $.name|$.username       Bret
    Integer     $.name|$.id             13  # the previous 1 is kept in enum!
    Object      $.name|$.id|$.company
    Missing     response body notexisting
    Missing     $.notexisting

JSONPath query from array
    GET         /users?_limit=5
    Array       $
    Object      $[0]
    Integer     $[0].id                 1
    Integer     $[1][id]                2
    Integer     $[4].id                 5
    Integer     $[*].id                 1   2   3   4   5
    Integer     $[*].id                 minimum=1   maximum=5
    String      $[*].name               minLength=10
    Object      $.[0]
    Integer     $.[0].id                1
    Integer     $.[4].id                5
    Integer     $.[*].id                1   2   3   4   5
    Object      $.[*]..lat.`parent`
    Integer     $.[*] where $.id
    Integer     $.[0:1].id|$.[1:4].id   1   2   3   4   5
    Missing     $[*].notexisting
