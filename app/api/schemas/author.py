# -*- coding:utf-8 -*-
"""
AuthorSchema module
"""

from loglan_core import Author, Word
from marshmallow_sqlalchemy.fields import Nested

from app.api.schemas import ma


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author
        include_fk = True
        exclude = ("created", "updated", "_contribution")

    _contribution = Nested("WordSchema", only=Word.attributes_basic(), many=True)
    contribution = _contribution


author_schema_nested = AuthorSchema(only=Author.attributes_basic())
author_schema_full = AuthorSchema(only=(*Author.attributes_extended(), "contribution"))

blue_print_export = (Author, author_schema_nested, author_schema_full)
