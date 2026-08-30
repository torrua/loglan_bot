"""Helper for formatting Loglan word definitions into HTML."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loglan_core import Definition


class DefinitionFormatter:
    """Additional methods for definition formatting."""

    def __init__(self, definition: Definition):
        self.d = definition

    @property
    def body_formatted(self) -> str:
        """Substitutes tags in the definition's body and formats punctuation."""
        to_key = "<k>"  # key
        tc_key = "</k>"
        to_log = "<l>"  # log
        tc_log = "</l>"

        body_str = str(self.d.body or "")
        return (
            body_str.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("«", to_key)
            .replace("»", tc_key)
            .replace("{", to_log)
            .replace("}", tc_log)
            .replace("...", "…")
            .replace("--", "—")
        )

    def highlight_key(self, key: str, case_sensitive: bool = False) -> str:
        """Highlights the current key from the list, deselecting the rest."""
        to_key = "<k>"
        tc_key = "</k>"
        to_del = "<do_not_delete>"
        tc_del = "</do_not_delete>"
        flag = re.IGNORECASE if not case_sensitive else 0
        key_pattern = re.compile(f"{to_key}{re.escape(key.replace('*', '.*'))}{tc_key}", flags=flag)
        def_body = key_pattern.sub(f"{to_del}\\g<0>{tc_del}", self.body_formatted)
        def_body = def_body.replace(tc_key, "").replace(to_key, "")
        def_body = def_body.replace(to_del, to_key).replace(tc_del, tc_key)

        return str(def_body)

    def tagged_word_origin_x(self, tag: str) -> str:
        """Generate Word.origin_x as HTML tag."""
        if (
            self.d.source_word
            and self.d.source_word.origin_x
            and self.d.source_word.type
            and self.d.source_word.type.group == "Cpx"
        ):
            return str(tag % self.d.source_word.origin_x)
        return ""

    def tagged_word_name(self, tag: str) -> str:
        """Generate Word.name as HTML tag."""
        if not self.d.source_word:
            return ""
        if not self.d.usage:
            return str(tag % self.d.source_word.name)
        return str(tag % self.d.usage.replace("%", self.d.source_word.name))

    def tagged_definition_body(self, key: str, tag: str) -> str:
        """Generate Definition's body as HTML tag with highlighted key word."""
        return str(tag % self.highlight_key(key))
