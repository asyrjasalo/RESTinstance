# -*- coding: utf-8 -*-

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
        "draft-04": ("enum", "type", "allOf", "anyOf", "oneOf", "not",
                   "definitions"),
        "draft-06": ("enum", "type", "allOf", "anyOf", "oneOf", "not",
                   "definitions", "const", "contains", "propertyNames"),
        "draft-07": ("enum", "type", "allOf", "anyOf", "oneOf", "not",
                   "definitions", "const", "contains", "propertyNames")
    },
    "integer": {
        "draft-04": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum"),
        "draft-06": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum"),
        "draft-07": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum")
    },
    "number": {
        "draft-04": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum"),
        "draft-06": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum"),
        "draft-07": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum")
    },
    "string": {
        "draft-04": ("format", "maxLength", "minLength", "pattern"),
        "draft-06": ("format", "maxLength", "minLength", "pattern"),
        "draft-07": ("format", "maxLength", "minLength", "pattern")
    },
    "object": {
        "draft-04": ("maxProperties", "minProperties", "required",
                   "additionalProperties", "properties",
                   "patternProperties", "dependencies"),
        "draft-06": ("maxProperties", "minProperties", "required",
                   "additionalProperties", "properties",
                   "patternProperties", "dependencies"),
        "draft-07": ("maxProperties", "minProperties", "required",
                   "additionalProperties", "properties",
                   "patternProperties", "dependencies")
    },
    "array": {
        "draft-04": ("additionalItems", "items", "maxItems", "minItems",
                   "uniqueItems"),
        "draft-06": ("additionalItems", "items", "maxItems", "minItems",
                   "uniqueItems"),
        "draft-07": ("additionalItems", "items", "maxItems", "minItems",
                   "uniqueItems")
    }
}
