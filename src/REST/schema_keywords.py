# -*- coding: utf-8 -*-

# RESTinstance (https://github.com/asyrjasalo/RESTinstance)
# Robot Framework library for RESTful JSON APIs.
#
# Copyright(C) 2018- Anssi Syrjäsalo (http://a.syrjasalo.com)
# Licensed under GNU Lesser General Public License v3 (LGPL-3.0).

GENSON_GENERATED_KEYWORDS = (
    "$schema",
    "anyOf",
    "items",
    "patternProperties",
    "properties",
    "required",
    "type",
)

SCHEMA_KEYWORDS = {
    "common": {
        "draft-04": (
            "enum",
            "type",
            "allOf",
            "anyOf",
            "oneOf",
            "not",
            "definitions",
        ),
        "draft-06": (
            "enum",
            "type",
            "allOf",
            "anyOf",
            "oneOf",
            "not",
            "definitions",
            "const",
            "contains",
            "propertyNames",
        ),
        "draft-07": (
            "enum",
            "type",
            "allOf",
            "anyOf",
            "oneOf",
            "not",
            "definitions",
            "const",
            "contains",
            "propertyNames",
        ),
    },
    "integer": {
        "draft-04": (
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        ),
        "draft-06": (
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        ),
        "draft-07": (
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        ),
    },
    "number": {
        "draft-04": (
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        ),
        "draft-06": (
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        ),
        "draft-07": (
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        ),
    },
    "string": {
        "draft-04": ("format", "maxLength", "minLength", "pattern"),
        "draft-06": ("format", "maxLength", "minLength", "pattern"),
        "draft-07": ("format", "maxLength", "minLength", "pattern"),
    },
    "object": {
        "draft-04": (
            "maxProperties",
            "minProperties",
            "required",
            "additionalProperties",
            "properties",
            "patternProperties",
            "dependencies",
        ),
        "draft-06": (
            "maxProperties",
            "minProperties",
            "required",
            "additionalProperties",
            "properties",
            "patternProperties",
            "dependencies",
        ),
        "draft-07": (
            "maxProperties",
            "minProperties",
            "required",
            "additionalProperties",
            "properties",
            "patternProperties",
            "dependencies",
        ),
    },
    "array": {
        "draft-04": (
            "additionalItems",
            "items",
            "maxItems",
            "minItems",
            "uniqueItems",
        ),
        "draft-06": (
            "additionalItems",
            "items",
            "maxItems",
            "minItems",
            "uniqueItems",
        ),
        "draft-07": (
            "additionalItems",
            "items",
            "maxItems",
            "minItems",
            "uniqueItems",
        ),
    },
}
