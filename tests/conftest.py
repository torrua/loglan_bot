"""Pytest Configuration and Shared Fixtures"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from app.main import create_app


@pytest.fixture
def test_app():
    """Creates a configured Quart test app instance."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def test_client(test_app) -> Any:
    """Returns a test client for the Quart application."""
    return test_app.test_client()


@pytest.fixture
def mock_word():
    """Returns a mock Word object matching Loglan-Core schema."""
    word = MagicMock()
    word.id = 42
    word.name = "kliri"
    word.match = "clear"
    word.rank = "1.0"
    word.origin = "kli"
    word.origin_x = None

    author_mock = MagicMock()
    author_mock.abbreviation = "L4"
    word.authors = [author_mock]

    year_mock = MagicMock()
    year_mock.year = 1975
    word.year = year_mock

    type_mock = MagicMock()
    type_mock.type_ = "C-Prim"
    type_mock.group = "Prim"
    word.type = type_mock

    affix_mock = MagicMock()
    affix_mock.name = "kli"
    word.affixes = [affix_mock]
    word.parents = []
    word.complexes = []

    def_mock = MagicMock()
    def_mock.id = 101
    def_mock.body = "G is «clear» than J, see {kliri}"
    def_mock.grammar = "(2a)"
    def_mock.grammar_code = "a"
    def_mock.slots = 2
    def_mock.case_tags = "G-J"
    def_mock.usage = ""
    def_mock.source_word = word
    word.definitions = [def_mock]

    return word


@pytest.fixture
def mock_definition(mock_word):
    """Returns a mock Definition object."""
    return mock_word.definitions[0]
