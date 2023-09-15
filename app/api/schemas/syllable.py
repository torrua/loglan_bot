# -*- coding:utf-8 -*-
"""
SyllableSchema module
"""

from loglan_core import Syllable

from api.schemas import ma


class SyllableSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Syllable
        exclude = ("created", "updated")


syllable_schema_nested = SyllableSchema(only=Syllable.attributes_basic())
syllable_schema_full = SyllableSchema(only=Syllable.attributes_extended())

blue_print_export = (Syllable, syllable_schema_nested, syllable_schema_full)
