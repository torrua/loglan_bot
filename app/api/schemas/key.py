# -*- coding:utf-8 -*-
"""
KeySchema module
"""

from loglan_core import Key, Definition
from marshmallow_sqlalchemy.fields import Nested

from app.api.schemas import ma


class KeySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Key
        include_fk = True
        exclude = (
            "created",
            "updated",
            "relationship_definitions",
        )

    _definitions = Nested(
        "DefinitionSchema",
        exclude=["word_id", "keys"],
        many=True,
        only={
            *Definition.attributes_basic(),
            *Definition.relationships(),
            "source_word",
        },
    )
    definitions = _definitions


key_schema_nested = KeySchema(only=Key.attributes_basic())
key_schema_full = KeySchema(only=(*Key.attributes_extended(), "definitions"))

blue_print_export = (Key, key_schema_nested, key_schema_full)
