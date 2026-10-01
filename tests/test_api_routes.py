"""Tests for LOD Manager REST API endpoints and authentication."""

from __future__ import annotations

import hashlib
import hmac
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.auth import validate_init_data


def generate_mock_init_data(bot_token: str, user_id: int = 1790409) -> str:
    """Helper to generate a cryptographically valid Telegram initData string."""
    auth_date = int(time.time())
    user_json = f'{{"id":{user_id},"first_name":"Test","username":"tester"}}'
    params = {
        "auth_date": str(auth_date),
        "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
        "user": user_json,
    }
    items = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in items)

    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    return f"auth_date={auth_date}&query_id={params['query_id']}&user={user_json}&hash={calc_hash}"


def test_auth_validate_init_data():
    token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    valid_data = generate_mock_init_data(token, user_id=123)
    is_valid, payload, err = validate_init_data(valid_data, token)
    assert is_valid is True
    assert payload is not None
    assert payload["user"]["id"] == 123
    assert err is None

    # Test tampering with payload
    tampered = valid_data.replace("123", "999")
    is_valid_t, _, err_t = validate_init_data(tampered, token)
    assert is_valid_t is False
    assert "Hash mismatch" in str(err_t)

    # Test wrong bot token
    is_valid_w, _, _ = validate_init_data(valid_data, "wrong_token")
    assert is_valid_w is False


@pytest.mark.asyncio
async def test_api_health(test_client):
    res = await test_client.get("/api/v1/health")
    assert res.status_code == 200
    data = await res.get_json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_api_types(test_client):
    mock_type = MagicMock()
    mock_type.id = 1
    mock_type.type_ = "C-Prim"
    mock_type.type_x = "C-Prim"
    mock_type.group = "Prim"
    mock_type.parentable = True
    mock_type.description = "Complex Predicate"

    with patch("app.api.routes.BaseSelector") as mock_selector_cls:
        instance = mock_selector_cls.return_value
        instance.all_async = AsyncMock(return_value=[mock_type])

        res = await test_client.get("/api/v1/types")
        assert res.status_code == 200
        types = await res.get_json()
        assert len(types) == 1
        assert types[0]["type"] == "C-Prim"
        assert types[0]["group"] == "Prim"


@pytest.mark.asyncio
async def test_api_events(test_client):
    mock_event = MagicMock()
    mock_event.id = 1
    mock_event.event_id = 1
    mock_event.name = "Initial"
    mock_event.date = "1975-01-01"
    mock_event.definition = "Def"
    mock_event.annotation = "Ann"
    mock_event.suffix = ""

    with patch("app.api.routes.BaseSelector") as mock_selector_cls:
        instance = mock_selector_cls.return_value
        instance.all_async = AsyncMock(return_value=[mock_event])

        res = await test_client.get("/api/v1/events")
        assert res.status_code == 200
        events = await res.get_json()
        assert len(events) == 1
        assert events[0]["name"] == "Initial"


@pytest.mark.asyncio
async def test_api_authors(test_client):
    mock_author = MagicMock()
    mock_author.id = 1
    mock_author.abbreviation = "JCB"
    mock_author.full_name = "James Cooke Brown"
    mock_author.notes = None

    with patch("app.api.routes.BaseSelector") as mock_selector_cls:
        instance = mock_selector_cls.return_value
        instance.all_async = AsyncMock(return_value=[mock_author])

        res = await test_client.get("/api/v1/authors")
        assert res.status_code == 200
        authors = await res.get_json()
        assert len(authors) == 1
        assert authors[0]["abbreviation"] == "JCB"


@pytest.mark.asyncio
async def test_api_word_detail_found(test_client, mock_word):
    mock_word.definitions = []
    mock_word.djifoa = []
    mock_word.spellings = []
    mock_word.complexes = []
    mock_word.parents = []
    mock_word.derivatives = []

    with patch(
        "app.api.routes.DictionaryService.get_word_by_id", AsyncMock(return_value=mock_word)
    ):
        res = await test_client.get("/api/v1/words/42")
        assert res.status_code == 200
        data = await res.get_json()
        assert data["id"] == 42
        assert data["name"] == "kliri"


@pytest.mark.asyncio
async def test_api_word_detail_not_found(test_client):
    with patch("app.api.routes.DictionaryService.get_word_by_id", AsyncMock(return_value=None)):
        res = await test_client.get("/api/v1/words/999999999")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_api_unauthorized_mutation(test_client):
    res = await test_client.post("/api/v1/words", json={"name": "testword"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_api_get_words_with_event_filter(test_client):
    mock_session = AsyncMock()
    mock_event = MagicMock()
    mock_event.event_id = 6
    mock_session.get = AsyncMock(return_value=mock_event)

    mock_row = (42, "kliri", "C-Prim", 2)
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.api.routes.async_session_maker") as mock_maker:
        mock_maker.return_value.__aenter__.return_value = mock_session
        res = await test_client.get("/api/v1/words?eventId=6")
        assert res.status_code == 200
        words = await res.get_json()
        assert len(words) == 1
        assert words[0]["id"] == 42
        assert words[0]["name"] == "kliri"
        assert words[0]["type_name"] == "C-Prim"
        assert words[0]["def_count"] == 2

