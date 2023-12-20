# -*- coding:utf-8 -*-
"""
TypeSchema module
"""

from loglan_core import Type, Word
from marshmallow_sqlalchemy.fields import Nested

from app.api.schemas import ma


class TypeSchema(ma.SQLAlchemyAutoSchema):  # pylint: disable=too-many-ancestors
    class Meta:
        model = Type
        include_fk = True
        exclude = ("created", "updated", "relationship_words")

    _words = Nested("WordSchema", only=Word.attributes_basic(), many=True)
    words = _words


type_schema_nested = TypeSchema(only=Type.attributes_basic())
type_schema_full = TypeSchema(only=(*Type.attributes_extended(), "words"))

blue_print_export = (Type, type_schema_nested, type_schema_full)
