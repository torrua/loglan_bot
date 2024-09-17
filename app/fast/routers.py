from __future__ import annotations

from loglan_core import (
    Word,
    Event,
    Definition,
    Type,
    Key,
    Setting,
    Syllable,
    Author,
)

from app.fast.models import (
    BaseDefinitionResponse,
    BaseWordResponse,
    BaseKeyResponse,
    BaseAuthorResponse,
    BaseTypeResponse,
    BaseEventResponse,
    BaseSettingResponse,
    BaseSyllableResponse,
    BaseDefinitionDetailedResponse,
    BaseWordDetailedResponse,
    BaseSettingDetailedResponse,
    BaseSyllableDetailedResponse,
)
from app.fast.base import (
    create_router,
)
from app.fast.validators import (
    word_validate_relationships,
    definition_validate_relationships,
    event_validate_relationships,
    type_validate_relationships,
    keys_validate_relationships,
    author_validate_relationships,
)

router_authors = create_router(
    orm_model=Author,
    base_response_model=BaseAuthorResponse,
    detailed_response_model=BaseAuthorResponse,
    validate_func=author_validate_relationships,
)

router_words = create_router(
    orm_model=Word,
    base_response_model=BaseWordResponse,
    detailed_response_model=BaseWordDetailedResponse,
    validate_func=word_validate_relationships,
)

router_definitions = create_router(
    orm_model=Definition,
    base_response_model=BaseDefinitionResponse,
    detailed_response_model=BaseDefinitionDetailedResponse,
    validate_func=definition_validate_relationships,
)

router_events = create_router(
    orm_model=Event,
    base_response_model=BaseEventResponse,
    detailed_response_model=BaseEventResponse,
    validate_func=event_validate_relationships,
)

router_types = create_router(
    orm_model=Type,
    base_response_model=BaseTypeResponse,
    detailed_response_model=BaseTypeResponse,
    validate_func=type_validate_relationships,
)

router_keys = create_router(
    orm_model=Key,
    base_response_model=BaseKeyResponse,
    detailed_response_model=BaseKeyResponse,
    validate_func=keys_validate_relationships,
)

router_settings = create_router(
    orm_model=Setting,
    base_response_model=BaseSettingResponse,
    detailed_response_model=BaseSettingDetailedResponse,
    validate_func=None,
)

router_syllables = create_router(
    orm_model=Syllable,
    base_response_model=BaseSyllableResponse,
    detailed_response_model=BaseSyllableDetailedResponse,
    validate_func=None,
)

routers = [
    router_authors,
    router_words,
    router_definitions,
    router_events,
    router_types,
    router_keys,
    router_settings,
    router_syllables,
]
