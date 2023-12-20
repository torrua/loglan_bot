# -*- coding: utf-8 -*-
"""
This module contains a HTMLExportWord Model
"""

from itertools import groupby
from typing import Iterator

from loglan_core import Word, Event, Definition
from loglan_core.addons.exporter import ExportWordConverter
from loglan_core.addons.word_selector import WordSelector
from sqlalchemy import Select

from app.site.compose import DEFAULT_HTML_STYLE, Item
from app.site.compose.definition_formatter import DefinitionFormatter


class Meaning(Item):
    def __init__(self, word: Word, style: str = DEFAULT_HTML_STYLE):
        self.word = word
        self.style = style
        self._ewc = ExportWordConverter(word)

    def export_definition_for_loglan(self, d: Definition) -> str:
        """
        style:
        :return:
        """
        tags = {
            # usage, gram, body, tags, definition
            "normal": [
                '<span class="du">%s</span> ',
                '<span class="dg">(%s)</span> ',
                '<span class="db">%s</span>',
                ' <span class="dt">[%s]</span>',
                f'<div class="definition log" id={d.id}>%s</div>',
            ],
            "ultra": [
                "<du>%s</du> ",
                "(%s) ",
                "%s",
                " [%s]",
                "<d>%s</d>",
            ],
        }
        t_d_usage, t_d_gram, t_d_body, t_d_tags, t_definition = tags[self.style]

        def_usage = t_d_usage % d.usage.replace("%", "—") if d.usage else ""
        gram_form = f"{d.slots or ''}" + d.grammar_code
        def_gram = t_d_gram % gram_form if gram_form else ""
        def_body = t_d_body % DefinitionFormatter(d).body_formatted
        def_tags = (
            t_d_tags % d.case_tags.replace("-", "&zwj;-&zwj;") if d.case_tags else ""
        )
        return t_definition % f"{def_usage}{def_gram}{def_body}{def_tags}"

    def html_origin(self):
        """
        Returns:
        """
        orig = self.word.origin
        orig_x = self.word.origin_x

        if not (orig or orig_x):
            return str()

        origin = self._compose_origin(orig, orig_x)

        if self.style == "normal":
            return f'<span class="m_origin">&lt;{origin}&gt;</span> '
        return f"<o>&lt;{origin}&gt;</o> "

    @staticmethod
    def _compose_origin(orig: str, orig_x: str) -> str:
        """
        Generate basic 'origin' string
        Args:
            orig:
            orig_x:

        Returns:

        """
        if orig_x:
            return f"{orig}={orig_x}" if orig else orig_x
        return orig

    def export_as_html(self) -> str:
        """
        Returns:
        """
        n_l = "\n"
        mid, technical, definitions, used_in = self.generate_meaning()
        if self.style == "normal":
            used_in_list = (
                f'<div class="used_in">Used In: ' f"{used_in}</div>\n</div>"
                if used_in
                else "</div>"
            )
            return (
                f'<div class="meaning" id="{mid}">\n'
                f'<div class="technical">{technical}</div>\n'
                f'<div class="definitions">{n_l}'
                f"{n_l.join(definitions)}\n</div>\n{used_in_list}"
            )

        used_in_list = f"<us>Used In: {used_in}</us>\n</m>" if used_in else "</m>"
        return (
            f"<m>\n<t>{technical}</t>\n"
            f"<ds>{n_l}"
            f"{n_l.join(definitions)}\n</ds>\n{used_in_list}"
        )

    def generate_meaning(self) -> tuple:
        """
        :return:
        """
        (
            html_affixes,
            html_match,
            html_rank,
            html_source,
            html_type,
            html_used_in,
            html_year,
            t_technical,
        ) = self.get_styled_values()

        html_tech = (
            t_technical % f"{html_match}{html_type}{html_source}{html_year}{html_rank}"
        )
        html_tech = f"{html_affixes}{self.html_origin()}{html_tech}"
        return self.word.id, html_tech, self.html_definitions(), html_used_in

    def html_definitions(self):
        """
        :return:
        """
        return [self.export_definition_for_loglan(d) for d in self.word.definitions]

    @staticmethod
    def _tagger(tag: str, value: str | None, default_value: str | None = str()):
        return tag % value if value else default_value

    def used_in_as_html(self) -> str:
        tags = {
            "normal": '<a class="m_cpx">%s</a>',
            "ultra": "<cpx>%s</cpx>",
        }
        return " |&nbsp;".join(
            sorted(
                {
                    tags[self.style] % cpx.name
                    for cpx in filter(None, self.word.complexes)
                }
            )
        )

    def get_styled_values(self) -> tuple:
        """

        Returns:

        """
        tags = {
            "normal": [
                '<span class="m_afx">%s</span> ',
                '<span class="m_match">%s</span> ',
                '<span class="m_rank">%s</span>',
                '<span class="m_author">%s</span> ',
                '<span class="m_type">%s</span> ',
                '<span class="m_use">%s</span>',
                '<span class="m_year">%s</span> ',
                '<span class="m_technical">%s</span>',
            ],
            "ultra": [
                "<afx>%s</afx> ",
                "%s ",
                "%s",
                "%s ",
                "%s ",
                "<use>%s</use>",
                "%s ",
                "<tec>%s</tec>",
            ],
        }

        values = [
            self._ewc.e_affixes,
            self.word.match,
            self.word.rank,
            self._ewc.e_source,
            self.word.type.type,
            self.used_in_as_html(),
            self._ewc.e_year,
            None,
        ]
        default_values = [
            str(),
            str(),
            str(),
            str(),
            str(),
            None,
            str(),
            tags[self.style][-1],
        ]

        return tuple(
            self._tagger(tag, value, default_value)
            for tag, value, default_value in zip(
                tags[self.style], values, default_values
            )
        )


class LoglanItem(Item):
    """
    LoglanItem Class
    """

    def __init__(self, words: list[Word], style: str = DEFAULT_HTML_STYLE):
        self.words = words
        self.style = style

    @staticmethod
    def query_select_words(
        name, case_sensitive: bool = False, event_id: Event | int | str = None
    ) -> Select:
        words = (
            WordSelector()
            .by_name(name=name, case_sensitive=case_sensitive)
            .by_event(event_id=event_id)
        )
        return words

    def export_as_html(self) -> str:
        word_template = {
            "normal": '<div class="word" wid="%s">\n'
            '<div class="word_line"><span class="word_name">%s</span>,</div>\n'
            '<div class="meanings">\n%s\n</div>\n</div>',
            "ultra": '<w wid="%s"><wl>%s,</wl>\n<ms>\n%s\n</ms>\n</w>',
        }
        word_name = self.words[0].name
        meanings = "\n".join(
            [Meaning(word, self.style).export_as_html() for word in self.words]
        )
        return word_template[self.style] % (word_name.lower(), word_name, meanings)


class Composer(Item):
    def __init__(self, words: list[Word], style: str = DEFAULT_HTML_STYLE):
        self.words = words
        self.style = style

    def group_iterator(self) -> Iterator[list[Word]]:
        grouped_words = groupby(self.words, lambda ent: ent.name)
        for _, linked_words in grouped_words:
            yield list(linked_words)

    def export_as_html(self) -> str:
        """
        Convert all words into one HTML string
        Args:
        Returns:

        """

        words_template = {
            "normal": '<div class="words">\n%s\n</div>\n',
            "ultra": "<ws>\n%s\n</ws>\n",
        }

        iterator = self.group_iterator()
        items = [
            LoglanItem(words_list, self.style).export_as_html()
            for words_list in iterator
        ]
        return words_template[self.style] % "\n".join(items)
