#  Copyright 2018-  Anssi Syrjäsalo
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

GENSON_GENERATED_KEYWORDS = ("$schema", "anyOf", "items", "patternProperties",
                             "properties", "required", "type")

SCHEMA_KEYWORDS = {
    "common": {
        "draft04": ("enum", "type", "allOf", "anyOf", "oneOf", "not",
                   "definitions"),
        "draft06": ("enum", "type", "allOf", "anyOf", "oneOf", "not",
                   "definitions", "const", "contains", "propertyNames")
    },
    "integer": {
        "draft04": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum"),
        "draft06": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum")
    },
    "number": {
        "draft04": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum"),
        "draft06": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum")
    },
    "string": {
        "draft04": ("format", "maxLength", "minLength", "pattern"),
        "draft06": ("format", "maxLength", "minLength", "pattern")
    },
    "object": {
        "draft04": ("maxProperties", "minProperties", "required",
                   "additionalProperties", "properties",
                   "patternProperties", "dependencies"),
        "draft06": ("maxProperties", "minProperties", "required",
                   "additionalProperties", "properties",
                   "patternProperties", "dependencies")
    },
    "array": {
        "draft04": ("additionalItems", "items", "maxItems", "minItems",
                   "uniqueItems"),
        "draft06": ("additionalItems", "items", "maxItems", "minItems",
                   "uniqueItems")
    }
}
