"""Tests for Quart web application routes"""

from unittest.mock import AsyncMock, patch

import pytest
from bs4 import BeautifulSoup


@pytest.mark.asyncio
async def test_index_route(test_client):
    response = await test_client.get("/")
    assert response.status_code == 200
    body = await response.get_data(as_text=True)
    assert "Loglan Documentation" in body


@pytest.mark.asyncio
async def test_home_route(test_client):
    response = await test_client.get("/site/home")
    assert response.status_code == 200
    body = await response.get_data(as_text=True)
    assert "Welcome to Loglan Online" in body
    assert "Online LOD Dictionary" in body


@pytest.mark.asyncio
async def test_how_to_read_route(test_client):
    response = await test_client.get("/site/how_to_read")
    assert response.status_code == 200
    body = await response.get_data(as_text=True)
    assert "How to Read an LOD Entry" in body


@pytest.mark.asyncio
async def test_articles_route_with_mock_site(test_client):
    mock_html = """
    <html><body>
        <h2><a name="articles"></a>Loglan Articles</h2>
        <ol><li><a href="test.html">Test Article</a><br>Description of article by Author.</li></ol>
    </body></html>
    """
    mock_soup = BeautifulSoup(mock_html, "lxml")

    with patch("app.site.routes.site_client.get_soup", AsyncMock(return_value=mock_soup)):
        response = await test_client.get("/site/articles")
        assert response.status_code == 200
        body = await response.get_data(as_text=True)
        assert "Test Article" in body
        assert "Author" in body


@pytest.mark.asyncio
async def test_proxy_article_route(test_client):
    mock_html = """
    <html><body>
        <h1>Test Article Title</h1>
        <p>This is article content.</p>
    </body></html>
    """
    mock_soup = BeautifulSoup(mock_html, "lxml")

    with patch("app.site.routes.site_client.get_soup", AsyncMock(return_value=mock_soup)):
        response = await test_client.get("/site/Articles/test.html")
        assert response.status_code == 200
        body = await response.get_data(as_text=True)
        assert "Test Article Title" in body
        assert "This is article content." in body


@pytest.mark.asyncio
async def test_submit_search_empty(test_client):
    response = await test_client.post("/site/submit_search", form={"word": ""})
    assert response.status_code == 200
    json_data = await response.get_json()
    assert json_data["result"] == "<div></div>"


@pytest.mark.asyncio
async def test_submit_search_loglan_found(test_client, mock_word):
    with patch(
        "app.services.dictionary.DictionaryService.get_words_by_name",
        AsyncMock(return_value=[mock_word]),
    ):
        response = await test_client.post(
            "/site/submit_search",
            form={"word": "kliri", "language_id": "log", "event_id": "1"},
        )
        assert response.status_code == 200
        json_data = await response.get_json()
        assert "kliri" in json_data["result"]


@pytest.mark.asyncio
async def test_submit_search_not_found(test_client):
    with patch(
        "app.services.dictionary.DictionaryService.get_words_by_name", AsyncMock(return_value=[])
    ):
        response = await test_client.post(
            "/site/submit_search",
            form={"word": "nonexistent", "language_id": "log"},
        )
        assert response.status_code == 200
        json_data = await response.get_json()
        assert "There is no word" in json_data["result"]


@pytest.mark.asyncio
async def test_404_handler(test_client):
    response = await test_client.get("/nonexistent-page-12345")
    assert response.status_code == 404
