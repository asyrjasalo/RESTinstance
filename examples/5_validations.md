# Validations

To validate output you can have following keywords:

* Missing
* Null
* Boolean
* Integer
* Number
* String
* Object
* Array

## Missing

Keyword `Missing` checks if the expected field does not exist.

Example usages:

| Keyword | Field | Remarks |
| ------- | ----------- | ------- |
| `GET`     | /users/1 | # https://jsonplaceholder.typicode.com/users/1 |
| `Missing` | response body password | |
| `Missing` | $.password | |
| `Missing` | $..geo.elevation | # response body address geo elevation |
| `GET`     | /users | # https://jsonplaceholder.typicode.com/users |
| `Missing` | response body 0 password | |
| `Missing` | $[*].password | |
| `Missing` | $[*]..geo.elevation | |

## Null

Keyword `Null` checks the expected field as JSON [null](https://en.wikipedia.org/wiki/Null_pointer)

Example usages:

| Keyword | Field | Remarks |
| ------- | ----------- | ------- |
| `PUT`  | /users/1 | { "deactivated_at": null } | # https://jsonplaceholder.typicode.com/users/1 |
| `Null` | response body deactivated_at | |
| `Null` | $.deactivated_at | | # JSONPath alternative |

## Boolean

Keyword `Boolean` checks the expected field  as JSON [boolean](https://en.wikipedia.org/wiki/Boolean_data_type).

Example usages:

| Keyword | Field | Value  | Arguments | Remarks |
| ------- | ----- | ------ | --------- | ------- |
| `PUT`  | /users/1 | { "verified_email": true } | | # https://jsonplaceholder.typicode.com/users/1 |
| `Boolean` | response body verified_email | | | # value is optional |
| `Boolean` | response body verified_email | true |
| `Boolean` | response body verified_email | ${True} | |# same as above |
| `Boolean` | $.verified_email | true | # JSONPath alternative |
| `Boolean` | $.verified_email | true | enum=[1, "1"] | skip=true |

## Integer

Keyword `Integer` checks the expected field as JSON [integer](https://en.wikipedia.org/wiki/Integer)

Example usages:

| Keyword | Field | Enum | Validations | Remarks |
| ------- | ----- | ---- | ----------- | ------- |
| `GET`  | /users/1 | | | # https://jsonplaceholder.typicode.com/users/1 |
| `Integer` | response body id | | | # value is optional |
| `Integer` | response body id | 1 |
| `Integer` | response body id | ${1} | | # same as above |
| `Integer` | $.id | 1 | | # JSONPath alternative |
| `GET`  | /users?_limit=10 | | | # https://jsonplaceholder.typicode.com/users |
| `Integer` | response body 0 id | 1 | | |
| `Integer` | $[0].id | 1 | | # same as above |
| `Integer` | $[*].id | | minimum=1 | maximum=10 |

## Number

Keyword `Number` checks the expected field as JSON number.

Example usages:

| Keyword | Field | Enum | Validations | Remarks |
| ------- | ----- | ---- | ----------- | ------- |
| `PUT`  | /users/1 | { "allocation": 95.0 } | | # https://jsonplaceholder.typicode.com/users/1 |
| `Number` | response body allocation | | | # value is optional |
| `Number` | response body allocation | 95.0 |
| `Number` | response body allocation | ${95.0} |  |# same as above |
| `Number` | $.allocation | 95.0 | | # JSONPath alternative |
| `GET`  | /users?_limit=10 | | | # https://jsonplaceholder.typicode.com/users |
| `Number` | $[0].id | 1 | | # integers are also numbers |
| `Number` | $[*].id | | minimum=1 | maximum=10 |

## String

Keyword `String` checks the expected field as JSON string.

Example usages:

| Keyword | Field | Enum | Validations | Remarks |
| ------- | ----- | ---- | ----------- | ------- |
| `GET`  | /users/1 | | | # https://jsonplaceholder.typicode.com/users/1 |
| `String` | response body email | | | # value is optional |
| `String` | response body email | Sincere@april.biz |
| `String` | $.email | Sincere@april.biz | | # JSONPath alternative |
| `String` | $.email | | format=email |
| `GET`  | /users?_limit=10 | | | # https://jsonplaceholder.typicode.com/users |
| `String` | response body 0 email | Sincere@april.biz |
| `String` | $[0].email | Sincere@april.biz | | # same as above |
| `String` | $[*].email | | format=email |

## Object

Keyword `Object` checks the expected field as JSON object.

Example usages:

| Keyword | Field | Enum | Validations | Remarks |
| ------- | ----- | ---- | ----------- | ------- |
| `GET`  | /users/1 | | | # https://jsonplaceholder.typicode.com/users/1 |
| `Object` | response body | |
| `Object` | response body | required=["id", "name"] | | # can have other properties |
| `GET`  | /users/1 | | | # https://jsonplaceholder.typicode.com/users/1 |
| `Object` | $.address.geo | required=["lat", "lng"] |
| `Object` | $..geo | additionalProperties=false | | # cannot have other properties |

## Array

Keyword `Array` checks the expected field as JSON array.
Keyword doesn't verify the contents of the array. You can use e.g. [Collections library](https://robotframework.org/robotframework/latest/libraries/Collections.html) to do that.

Example usages:

| Keyword | Field | Enum | Validations | Remarks |
| ------- | ----- | ---- | ----------- | ------- |
| `GET`  | /users?_limit=10 | | | # https://jsonplaceholder.typicode.com/users |
| `Array` | response body | | |
| `Array` | $ | | | | # same as above |
| `Array` | $ | minItems=1 | maxItems=10 | uniqueItems=true |
