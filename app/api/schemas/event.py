# -*- coding:utf-8 -*-
"""
EventSchema module
"""

from loglan_core import Event, Word
from marshmallow_sqlalchemy.fields import Nested

from app.api.schemas import ma


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_fk = True
        exclude = (
            "created",
            "updated",
            "relationship_deprecated_words",
            "relationship_appeared_words",
        )

    _appeared_words = Nested("WordSchema", only=Word.attributes_basic(), many=True)
    appeared_words = _appeared_words
    _deprecated_words = Nested("WordSchema", only=Word.attributes_basic(), many=True)
    deprecated_words = _deprecated_words


event_schema_nested = EventSchema(only=Event.attributes_basic())
event_schema_full = EventSchema(
    only=(*Event.attributes_extended(), "appeared_words", "deprecated_words")
)

blue_print_export = (Event, event_schema_nested, event_schema_full)
