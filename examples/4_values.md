# Values

Most keywords accept values as arguments in the following formats:

- JSON
- Dictionary
- File
- Bytes

**NOTE:** Depending on how you want to use your data, you might need to use `body` **or**
`data` argument.

## Body

The `body` argument is _only_ for JSON style payloads for the request. `body` arguments
can be JSON, dicitonary, or files containing JSON.

Example usage:

| Keyword | Field | Arguments | Remarks |
| ------- | ----- | --------- | ------- |
| Get | /users/1 | | Get doesn't allow the use of `body` |
| Post | /users/1 | {"name": "Harrison Ford" } |
| Post | /users/1 | ${my_dict} | `${my_dict}` is a dictionary object |
| Post | /users/1 | ${my_file} | `${my_file}` is the file name for a file that contains _only_ JSON data |

See more examples in [atest/methods.robot](../atest/methods.robot) file.

## Data

The `data` argument can be a dictionary, bytes or a file name. Note that the contents of the
file is read as bytes.

Example usage:

| Keyword | Field | Arguments | Remarks |
| ------- | ----- | --------- | ------- |
| Get | /users/1 | data=${my_dict} | |
| ${bytes}= Encode String to Bytes | ${some_string} | | `Encode String to Bytes` is from `String` library |
| Post | /users/1 | data=${bytes} | `${bytes}` |
| Post | /users/1 | ${my_file} | |

## Using Output values

All output from `Output` keyword is converted into a string and into a JSON string, when possible.
This means that for instance if your response body contains bytes, you will need to convert those
to bytes separately.

There is an [open ticket](https://github.com/asyrjasalo/RESTinstance/issues/121) to support other
forms of output data based on response headers.
