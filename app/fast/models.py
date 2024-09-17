from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, List

from pydantic import BaseModel, constr


class Base(BaseModel):
    id: int

    class Config:
        from_attributes = True


class BaseWordResponse(Base):
    name: str
    type_id: int
    event_start_id: int
    event_end_id: Optional[int]
    tid_old: Optional[int]
    origin: Optional[constr(max_length=128)]
    origin_x: Optional[constr(max_length=64)]
    match: Optional[constr(max_length=8)]
    rank: Optional[constr(max_length=8)]
    year: Optional[datetime]
    notes: Optional[Dict[str, str]]


class BaseDefinitionResponse(Base):
    word_id: int
    position: int
    body: str
    usage: Optional[constr(max_length=64)]
    grammar_code: Optional[constr(max_length=8)]
    slots: Optional[int]
    case_tags: Optional[constr(max_length=16)]
    language: Optional[constr(max_length=16)]
    notes: Optional[constr(max_length=255)]


class BaseAuthorResponse(Base):
    abbreviation: constr(max_length=64)
    full_name: Optional[constr(max_length=64)]
    notes: Optional[constr(max_length=128)]


class BaseTypeResponse(Base):
    type_: constr(max_length=16)
    type_x: constr(max_length=16)
    group: constr(max_length=16)
    parentable: bool
    description: Optional[constr(max_length=255)]


class BaseEventResponse(Base):
    event_id: int
    name: constr(max_length=64)
    date: datetime
    definition: str
    annotation: constr(max_length=16)
    suffix: constr(max_length=16)


class BaseKeyResponse(Base):
    word: constr(max_length=64)
    language: constr(max_length=16)


class BaseSettingResponse(Base):
    date: datetime
    db_version: int
    last_word_id: int
    db_release: constr(max_length=16)


class BaseSyllableResponse(Base):
    name: constr(max_length=8)
    type_: constr(max_length=32)
    allowed: bool


class BaseAuthorDetailedResponse(BaseAuthorResponse):
    contribution: List[BaseWordResponse] = []


class BaseDefinitionDetailedResponse(BaseDefinitionResponse):
    source_word: BaseWordResponse
    keys: List[BaseKeyResponse] = []


class BaseEventDetailedResponse(BaseEventResponse):
    deprecated_words: List[BaseWordResponse] = []
    appeared_words: List[BaseWordResponse] = []


class BaseKeyDetailedResponse(BaseKeyResponse):
    definitions: List[BaseDefinitionResponse] = []


class BaseTypeDetailedResponse(BaseTypeResponse):
    words: List[BaseWordResponse] = []


class BaseWordDetailedResponse(BaseWordResponse):
    authors: List[BaseAuthorResponse]
    type: BaseTypeResponse
    event_start: BaseEventResponse
    event_end: Optional[BaseEventResponse] = None
    definitions: List[BaseDefinitionResponse]
    derivatives: List[BaseWordResponse] = []
    affixes: List[BaseWordResponse] = []
    complexes: List[BaseWordResponse] = []


class BaseSettingDetailedResponse(BaseSettingResponse):
    pass


class BaseSyllableDetailedResponse(BaseSyllableResponse):
    pass
