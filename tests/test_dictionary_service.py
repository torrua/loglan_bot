"""Tests for DictionaryService layer with caching"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.services.dictionary import DictionaryService


@pytest.fixture(autouse=True)
def clear_dict_cache():
    """Clears dictionary cache before each test."""
    DictionaryService.clear_cache()
    yield
    DictionaryService.clear_cache()


@pytest.mark.asyncio
async def test_get_words_by_name(mock_word):
    with patch("app.services.dictionary.WordSelector") as mock_selector_cls:
        selector_instance = mock_selector_cls.return_value
        selector_instance.with_relationships.return_value = selector_instance
        selector_instance.by_name.return_value = selector_instance
        selector_instance.all_async = AsyncMock(return_value=[mock_word])

        words = await DictionaryService.get_words_by_name("kliri")
        assert len(words) == 1
        assert words[0].name == "kliri"
        assert selector_instance.all_async.call_count == 1

        # Second call should use cache and not hit DB
        cached_words = await DictionaryService.get_words_by_name("kliri")
        assert len(cached_words) == 1
        assert selector_instance.all_async.call_count == 1


@pytest.mark.asyncio
async def test_get_word_by_id(mock_word):
    with patch("app.services.dictionary.WordSelector") as mock_selector_cls:
        selector_instance = mock_selector_cls.return_value
        selector_instance.filter_by.return_value = selector_instance
        selector_instance.with_relationships.return_value = selector_instance
        selector_instance.scalar_async = AsyncMock(return_value=mock_word)

        word = await DictionaryService.get_word_by_id(42)
        assert word is not None
        assert word.id == 42
        assert selector_instance.scalar_async.call_count == 1

        # Second call should use cache
        cached_word = await DictionaryService.get_word_by_id(42)
        assert cached_word is not None
        assert selector_instance.scalar_async.call_count == 1


@pytest.mark.asyncio
async def test_get_definitions_by_key(mock_definition):
    with patch("app.services.dictionary.DefinitionSelector") as mock_selector_cls:
        selector_instance = mock_selector_cls.return_value
        selector_instance.with_relationships.return_value = selector_instance
        selector_instance.by_key.return_value = selector_instance
        selector_instance.all_async = AsyncMock(return_value=[mock_definition])

        defs = await DictionaryService.get_definitions_by_key("clear")
        assert len(defs) == 1
        assert defs[0].id == 101


@pytest.mark.asyncio
async def test_get_events_map():
    mock_events = [
        SimpleNamespace(id=1, name="LOD 1.0"),
        SimpleNamespace(id=2, name="LOD 2.0"),
    ]
    with patch("app.services.dictionary.BaseSelector") as mock_base_selector_cls:
        selector_instance = mock_base_selector_cls.return_value
        selector_instance.all_async = AsyncMock(return_value=mock_events)

        events = await DictionaryService.get_events_map()
        assert events == {2: "LOD 2.0", 1: "LOD 1.0"}
        assert selector_instance.all_async.call_count == 1

        # Second call uses cached dictionary
        cached_events = await DictionaryService.get_events_map()
        assert cached_events == {2: "LOD 2.0", 1: "LOD 1.0"}
        assert selector_instance.all_async.call_count == 1
