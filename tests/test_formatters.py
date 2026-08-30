"""Tests for message and HTML formatters"""

from app.bot.telegram.models import export, export_as_str
from app.site.compose.definition_formatter import DefinitionFormatter
from app.site.compose.english_item import EnglishItem
from app.site.compose.loglan_item import Composer, LoglanItem


def test_telegram_export(mock_definition):
    text = export(mock_definition)
    assert "<code>kliri</code>" in text
    assert "<i>clear</i>" in text
    assert "(2a)" in text
    assert "[G-J]" in text


def test_telegram_export_as_str(mock_word):
    text = export_as_str(mock_word)
    assert "<b>kliri</b> (kli)," in text
    assert "C-Prim" in text
    assert "'75" in text
    assert "1.0" in text


def test_definition_formatter(mock_definition):
    formatter = DefinitionFormatter(mock_definition)
    formatted_body = formatter.body_formatted
    assert "<l>kliri</l>" in formatted_body
    assert "<k>clear</k>" in formatted_body

    highlighted = formatter.highlight_key("clear")
    assert "<k>clear</k>" in highlighted


def test_english_item(mock_definition):
    item = EnglishItem(definitions=[mock_definition], key="clear", style="normal")
    html = item.export_as_html()
    assert "kliri" in html
    assert '<div class="d_line">' in html


def test_loglan_item(mock_word):
    item = LoglanItem(words=[mock_word], style="normal")
    html = item.export_as_html()
    assert 'wid="kliri"' in html
    assert "kliri" in html


def test_composer(mock_word):
    composer = Composer(words=[mock_word], style="normal")
    html = composer.export_as_html()
    assert '<div class="words">' in html
    assert "kliri" in html
