# -*- coding:utf-8 -*-
"""
TypeSchema module
"""

from loglan_core import Type, Word
from marshmallow_sqlalchemy.fields import Nested

from api.schemas import ma


class TypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Type
        include_fk = True
        exclude = ("created", "updated", "_words")

    _words = Nested("WordSchema", only=Word.attributes_basic(), many=True)
    words = _words


type_schema_nested = TypeSchema(only=Type.attributes_basic())
type_schema_full = TypeSchema(only=(*Type.attributes_extended(), "words"))

blue_print_export = (Type, type_schema_nested, type_schema_full)
