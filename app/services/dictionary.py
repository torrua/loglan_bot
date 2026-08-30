"""Dictionary Service Layer for LOD Database Access with In-Memory Caching"""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from loglan_core import BaseSelector, Definition, DefinitionSelector, Event, Word, WordSelector
from sqlalchemy.orm import joinedload

from app.engine import async_session_maker

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


class _LRUCache(Generic[T]):
    """Lightweight bounded LRU in-memory cache."""

    def __init__(self, maxsize: int = 512):
        self._maxsize = maxsize
        self._cache: OrderedDict[Any, T] = OrderedDict()

    def get(self, key: Any) -> T | None:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: Any, value: T) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._maxsize:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()


class DictionaryService:
    """Service providing high-level async query interface with in-memory caching."""

    _events_cache: dict[int, str] | None = None
    _words_by_name_cache: _LRUCache[Sequence[Word]] = _LRUCache(maxsize=512)
    _word_by_id_cache: _LRUCache[Word] = _LRUCache(maxsize=512)
    _definitions_by_key_cache: _LRUCache[Sequence[Definition]] = _LRUCache(maxsize=512)

    @classmethod
    def clear_cache(cls) -> None:
        """Clears all in-memory query and events caches."""
        cls._events_cache = None
        cls._words_by_name_cache.clear()
        cls._word_by_id_cache.clear()
        cls._definitions_by_key_cache.clear()

    @classmethod
    async def get_words_by_name(
        cls,
        name: str,
        case_sensitive: bool = False,
        event_id: int | None = None,
    ) -> Sequence[Word]:
        """Fetch Loglan words matching the given name with loaded relationships (cached)."""
        cache_key = (name.strip(), case_sensitive, event_id)
        if (cached := cls._words_by_name_cache.get(cache_key)) is not None:
            return cached

        async with async_session_maker() as session:
            selector = (
                WordSelector(case_sensitive=case_sensitive).with_relationships().by_name(name=name)
            )
            if event_id is not None:
                selector = selector.by_event(event_id=event_id)

            words = await selector.all_async(session, unique=True)
            result: Sequence[Word] = words or []
            cls._words_by_name_cache.set(cache_key, result)
            return result

    @classmethod
    async def get_word_by_id(cls, word_id: int) -> Word | None:
        """Fetch a single Loglan word by its record ID (cached)."""
        if (cached := cls._word_by_id_cache.get(word_id)) is not None:
            return cached

        async with async_session_maker() as session:
            word = await (
                WordSelector().filter_by(id=word_id).with_relationships().scalar_async(session)
            )
            if word is not None:
                cls._word_by_id_cache.set(word_id, word)
            return word

    @classmethod
    async def get_definitions_by_key(
        cls,
        key: str,
        language: str | None = None,
        case_sensitive: bool = False,
        event_id: int | None = None,
    ) -> Sequence[Definition]:
        """Fetch definitions matching a search key in English or another language (cached)."""
        cache_key = (key.strip(), language, case_sensitive, event_id)
        if (cached := cls._definitions_by_key_cache.get(cache_key)) is not None:
            return cached

        async with async_session_maker() as session:
            selector = (
                DefinitionSelector(case_sensitive=case_sensitive)
                .with_relationships("source_word")
                .by_key(key=key, language=language)
            )
            # Ensure source_word.type is also eagerly loaded
            selector.get_statement().options(
                joinedload(Definition.source_word).joinedload(Word.type)
            )

            if event_id is not None:
                selector = selector.by_event(event_id=event_id)

            definitions = await selector.all_async(session, unique=True)
            result: Sequence[Definition] = definitions or []
            cls._definitions_by_key_cache.set(cache_key, result)
            return result

    @classmethod
    async def get_events_map(cls) -> dict[int, str]:
        """Fetch all dictionary editions/events as a mapping of id -> name (cached)."""
        if cls._events_cache is not None:
            return cls._events_cache

        async with async_session_maker() as session:
            events = await BaseSelector(model=Event).all_async(session)
            cls._events_cache = {int(event.id): event.name for event in reversed(events)}
            return cls._events_cache
