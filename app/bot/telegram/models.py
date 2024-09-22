# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from collections import defaultdict

from loglan_core import Definition
from loglan_core.addons.definition_selector import DefinitionSelector

from app.engine import Session


def export(definition: Definition) -> str:
    """
    Convert definition's data to str for sending as a telegram messages
    :return: Adopted for posting in telegram string
    """
    d_usage = (
        f"<b>{definition.usage.replace('%', '—')}</b> " if definition.usage else ""
    )
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
    return f"{d_usage}{definition.grammar} {d_body}{d_case_tags}"


def format_affixes(word):
    return (
        f" ({' '.join([w.name for w in word.affixes]).strip()})" if word.affixes else ""
    )


def format_year(word):
    return "'" + str(word.year.year)[-2:] + " " if word.year else ""


def format_origin(word):
    if word.origin or word.origin_x:
        return (
            f"\n<i>&#60;{word.origin}"
            f"{' = ' + word.origin_x if word.origin_x else ''}&#62;</i>"
        )
    return ""


def format_authors(word):
    return (
        "/".join([a.abbreviation for a in word.authors]) + " " if word.authors else ""
    )


def format_rank(word):
    return word.rank + " " if word.rank else ""


def format_definitions(word):
    return "\n\n".join([export(d) for d in word.definitions])


def export_as_str(word) -> str:
    """
    Convert word's data to str for sending as a telegram messages
    :return: List of str with technical info, definitions, used_in part
    """
    w_affixes = format_affixes(word)
    w_match = word.match + " " if word.match else ""
    w_year = format_year(word)
    w_orig = format_origin(word)
    w_authors = format_authors(word)
    w_type = word.type.type_ + " "
    w_rank = format_rank(word)

    word_str = (
        f"<b>{word.name}</b>{w_affixes},"
        f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"
    )
    w_definitions = format_definitions(word)
    return f"{word_str}\n\n{w_definitions}"


def translation_by_key(request: str, language: str = None) -> str:
    """
    We get information about loglan words by key in a foreign language
    :param request: Requested string
    :param language: Key language
    :return: Search results string formatted for sending to Telegram
    """

    result = defaultdict(list)
    with Session() as session:
        definitions_result = (
            DefinitionSelector()
            .by_key(key=request, language=language)
            .with_relationships("source_word")
            .get_statement()
        )
        definitions = session.scalars(definitions_result).unique().all()
        for definition in definitions:
            result[definition.source_word.name].append(export(definition))

    new = "\n"
    word_items = [
        f"/{word_name},\n{new.join(definitions)}\n"
        for word_name, definitions in result.items()
    ]
    return new.join(word_items).strip()
