# -*- coding:utf-8 -*-
"""
WordSchema module
"""

from loglan_core import Word, Definition, Type, Author, Event
from marshmallow import fields
from marshmallow_sqlalchemy.fields import Nested

from app.api.schemas import ma
from app.api.schemas.author import AuthorSchema
from app.api.schemas.definition import DefinitionSchema
from app.api.schemas.event import EventSchema
from app.api.schemas.type import TypeSchema

nested_exclude = {
    "notes",
    "tid_old",
}
full_include = {
    "event_end",
    "authors",
    "definitions",
    "type",
    "event_start",
    "derivatives",
    "parents",
}


class WordSchema(ma.SQLAlchemyAutoSchema):  # pylint: disable=too-many-ancestors
    class Meta:
        model = Word
        include_fk = True
        exclude = (
            "created",
            "updated",
            "relationship_event_end",
            "relationship_authors",
            "relationship_definitions",
            "relationship_derivatives",
            "relationship_type",
            "relationship_event_start",
            "relationship_parents",
        )
        load_instance = True

    year = fields.Function(lambda obj: int(obj.year.strftime("%Y")))
    _authors = Nested(AuthorSchema(only=Author.attributes_basic()), many=True)
    authors = _authors

    _type = Nested(TypeSchema(only=Type.attributes_basic()))
    type = _type

    _event_start = Nested(EventSchema(only=Event.attributes_basic()))
    event_start = _event_start

    _event_end = Nested(EventSchema(only=Event.attributes_basic()))
    event_end = _event_end

    _definitions = Nested(
        DefinitionSchema(only=Definition.attributes_all()),
        exclude={
            "source_word",
        },
        many=True,
    )
    definitions = _definitions

    _parents = Nested(
        lambda: WordSchema,
        only=Word.attributes_basic(),
        exclude=nested_exclude,
        many=True,
    )
    parents = _parents

    _derivatives = Nested(
        lambda: WordSchema,
        only=Word.attributes_basic(),
        exclude=nested_exclude,
        many=True,
    )
    derivatives = _derivatives


word_schema_nested = WordSchema(only=Word.attributes_basic(), exclude=nested_exclude)
word_schema_full = WordSchema(only=(*Word.attributes_extended(), *full_include))

blue_print_export = (Word, word_schema_nested, word_schema_full)
