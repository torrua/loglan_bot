from __future__ import annotations

from app.fast.models import (
    BaseWordResponse,
    BaseDefinitionResponse,
    BaseAuthorResponse,
    BaseTypeResponse,
    BaseEventResponse,
    BaseKeyResponse,
)


async def word_validate_relationships(response, item):
    response.derivatives = [
        BaseWordResponse.model_validate(i) for i in item.derivatives
    ]
    response.affixes = [BaseWordResponse.model_validate(i) for i in item.affixes]
    response.affixes = [BaseWordResponse.model_validate(i) for i in item.complexes]
    response.definitions = [
        BaseDefinitionResponse.model_validate(i) for i in item.definitions
    ]
    response.authors = [BaseAuthorResponse.model_validate(i) for i in item.authors]
    response.type = BaseTypeResponse.model_validate(item.type)
    response.event_start = BaseEventResponse.model_validate(item.event_start)
    if item.event_end_id:
        response.event_end = BaseEventResponse.model_validate(item.event_end)


async def definition_validate_relationships(response, definition):
    response.source_word = BaseWordResponse.model_validate(definition.source_word)
    response.keys = [BaseKeyResponse.model_validate(key) for key in definition.keys]


async def event_validate_relationships(response, item):
    response.deprecated_words = [
        BaseWordResponse.model_validate(i) for i in item.deprecated_words
    ]
    response.deprecated_words = [
        BaseWordResponse.model_validate(i) for i in item.appeared_words
    ]


async def type_validate_relationships(response, item):
    response.words = [BaseWordResponse.model_validate(i) for i in item.words]


async def keys_validate_relationships(response, item):
    response.definitions = [
        BaseDefinitionResponse.model_validate(i) for i in item.definitions
    ]


async def author_validate_relationships(response, item):
    response.contribution = [
        BaseWordResponse.model_validate(i) for i in item.contribution
    ]
