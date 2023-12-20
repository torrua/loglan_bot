# -*- coding: utf-8 -*-

import re

from loglan_core import Definition


class DefinitionFormatter:
    """
    Additional methods for definition's formatting
    """

    def __init__(self, definition: Definition):
        self.d = definition

    @property
    def body_formatted(self) -> str:
        """
        Substitutes tags in the definition's body
        Formats punctuation signs
        :return:
        """
        to_key = "<k>"  # key
        tc_key = "</k>"
        to_log = "<l>"  # log
        tc_log = "</l>"

        return (
            self.d.body.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("«", to_key)
            .replace("»", tc_key)
            .replace("{", to_log)
            .replace("}", tc_log)
            .replace("...", "…")
            .replace("--", "—")
        )

    def highlight_key(self, key: str, case_sensitive: bool = False) -> str:
        """
        Highlights the current key from the list, deselecting the rest
        :param key:
        :param case_sensitive:
        :return:
        """
        to_key = "<k>"
        tc_key = "</k>"
        to_del = "<do_not_delete>"
        tc_del = "</do_not_delete>"
        flag = re.IGNORECASE if not case_sensitive else 0
        key_pattern = re.compile(
            f"{to_key}{re.escape(key.replace('*', '.*'))}{tc_key}", flags=flag
        )
        def_body = key_pattern.sub(f"{to_del}\\g<0>{tc_del}", self.body_formatted)
        def_body = def_body.replace(tc_key, "").replace(to_key, "")
        def_body = def_body.replace(to_del, to_key).replace(tc_del, tc_key)

        return def_body

    def tagged_word_origin_x(self, tag: str) -> str:
        """
        Generate Word.origin_x as HTML tag
        Args:
            tag:

        Returns:

        """
        return (
            tag % self.d.source_word.origin_x
            if (self.d.source_word.origin_x and self.d.source_word.type.group == "Cpx")
            else str()
        )

    def tagged_word_name(self, tag: str) -> str:
        """
        Generate Word.name as HTML tag
        Args:
            tag:

        Returns:

        """
        return (
            tag % self.d.source_word.name
            if not self.d.usage
            else tag % self.d.usage.replace("%", self.d.source_word.name)
        )

    def tagged_definition_body(self, key: str, tag: str) -> str:
        """
        Generate Definition's body as HTML tag with highlighted key word
        Args:
            key:
            tag:

        Returns:

        """
        return tag % self.highlight_key(key)
