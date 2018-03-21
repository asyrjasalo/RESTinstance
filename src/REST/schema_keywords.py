GENSON_GENERATED_KEYWORDS = ("$schema", "anyOf", "items", "patternProperties",
                             "properties", "required", "type")

SCHEMA_KEYWORDS = {
    "common": {
        "draft04": ("enum", "type", "allOf", "anyOf", "oneOf", "not",
                   "definitions")
    },
    "integer": {
        "draft04": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum")
    },
    "number": {
        "draft04": ("multipleOf", "maximum", "exclusiveMaximum", "minimum",
                   "exclusiveMinimum")
    },
    "string": {
        "draft04": ("format", "maxLength", "minLength", "pattern")
    },
    "object": {
        "draft04": ("maxProperties", "minProperties", "required",
                   "additionalProperties", "properties",
                   "patternProperties", "dependencies")
    },
    "array": {
        "draft04": ("additionalItems", "items", "maxItems", "minItems",
                   "uniqueItems")
    }
}
