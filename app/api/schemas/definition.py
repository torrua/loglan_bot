# -*- coding:utf-8 -*-
"""
DefinitionSchema module
"""

from loglan_core import Definition, Word, Key
from marshmallow_sqlalchemy.fields import Nested

from app.api.schemas import ma
from app.api.schemas.key import KeySchema


class DefinitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Definition
        include_fk = True
        exclude = ("created", "updated", "_keys", "_source_word")

    _source_word = Nested("WordSchema", only=Word.attributes_basic())
    source_word = _source_word

    _keys = Nested(KeySchema, only=Key.attributes_basic(), many=True)
    keys = _keys


definition_schema_nested = DefinitionSchema(
    only=(*Definition.attributes_basic(), "source_word")
)
definition_schema_full = DefinitionSchema(
    only=(*Definition.attributes_extended(), "keys", "source_word")
)

blue_print_export = (Definition, definition_schema_nested, definition_schema_full)
