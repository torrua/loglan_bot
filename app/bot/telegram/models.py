"""Formatting and Export Models for Telegram Bot Messages"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from app.services.dictionary import DictionaryService

if TYPE_CHECKING:
    from loglan_core import Definition, Word


def export(definition: Definition) -> str:
    """Convert definition's data to str for sending as a telegram message."""
    d_usage = f"<b>{definition.usage.replace('%', '—')}</b> " if definition.usage else ""
    d_body = (
        definition.body.replace("<", "&#60;")
        .replace(">", "&#62;")
        .replace("«", "<i>")
        .replace("»", "</i>")
        .replace("{", "<code>")
        .replace("}", "</code>")
        .replace("....", "….")
        .replace("...", "…")
        .replace("--", "—")
    )

    d_case_tags = f" [{definition.case_tags}]" if definition.case_tags else ""
    grammar = definition.grammar or ""
    return f"{d_usage}{grammar} {d_body}{d_case_tags}".strip()


def format_affixes(word: Word) -> str:
    """Format short affix names (djifoa) in parentheses."""
    if word.affixes:
        return f" ({' '.join([w.name for w in word.affixes if w])})"
    return ""


def format_year(word: Word) -> str:
    """Format 2-digit year."""
    return f"'{str(word.year.year)[-2:]} " if word.year else ""


def format_origin(word: Word) -> str:
    """Format word origin and components."""
    if word.origin or word.origin_x:
        origin_x_part = f" = {word.origin_x}" if word.origin_x else ""
        return f"\n<i>&#60;{word.origin or ''}{origin_x_part}&#62;</i>"
    return ""


def format_authors(word: Word) -> str:
    """Format author initials."""
    if word.authors:
        return "/".join([a.abbreviation for a in word.authors if a]) + " "
    return ""


def format_rank(word: Word) -> str:
    """Format semantic frequency rank."""
    return f"{word.rank} " if word.rank else ""


def format_definitions(word: Word) -> str:
    """Format all definitions of a word."""
    return "\n\n".join([export(d) for d in word.definitions])


def export_as_str(word: Word) -> str:
    """Convert word's data to a full string formatted for Telegram."""
    w_affixes = format_affixes(word)
    w_match = f"{word.match} " if word.match else ""
    w_year = format_year(word)
    w_orig = format_origin(word)
    w_authors = format_authors(word)
    w_type = f"{word.type.type_} " if word.type else ""
    w_rank = format_rank(word)

    word_str = (
        f"<b>{word.name}</b>{w_affixes},\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"
    )
    w_definitions = format_definitions(word)
    return f"{word_str}\n\n{w_definitions}".strip()


async def translation_by_key(request: str, language: str | None = None) -> str:
    """Get information about Loglan words by key in a foreign language."""
    result: dict[str, list[str]] = defaultdict(list)
    definitions = await DictionaryService.get_definitions_by_key(
        key=request,
        language=language,
    )

    for definition in definitions:
        if definition.source_word:
            result[definition.source_word.name].append(export(definition))

    word_items = [
        f"/{word_name},\n" + "\n".join(def_list) + "\n" for word_name, def_list in result.items()
    ]
    return "\n".join(word_items).strip()
