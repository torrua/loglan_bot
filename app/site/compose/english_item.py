"""English-to-Loglan HTML Presentation Model"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.site.compose import DEFAULT_HTML_STYLE, Item
from app.site.compose.definition_formatter import DefinitionFormatter

if TYPE_CHECKING:
    from loglan_core import Definition


class EnglishItem(Item):
    """Formats English-to-Loglan search results into HTML."""

    def __init__(
        self,
        definitions: Sequence[Definition],
        key: str,
        style: str = DEFAULT_HTML_STYLE,
    ):
        self.definitions = definitions
        self.key = key
        self.style = style

    def export_as_html(self) -> str:
        return "\n".join(
            [self.export_for_english(d, self.key, self.style) for d in self.definitions]
        )

    @staticmethod
    def export_for_english(
        definition: Definition,
        key: str,
        style: str = DEFAULT_HTML_STYLE,
    ) -> str:
        tags = {
            "normal": [
                '<span class="dg">(%s)</span>',
                '<span class="dt">[%s]</span> ',
                ' <span class="db">%s</span>',
                f'<span class="definition eng" id={definition.id}>%s</span>',
                '<div class="d_line">%s</div>',
                '<span class="w_name">%s</span>, ',
                '<span class="w_origin">&lt;%s&gt;</span> ',
            ],
            "ultra": [
                "(%s)",
                "[%s] ",
                " %s",
                "<de>%s</de>",
                "<ld>%s</ld>",
                "<wn>%s</wn>, ",
                "<o>&lt;%s&gt;</o> ",
            ],
        }

        style_tags = tags.get(style, tags["normal"])
        (
            t_d_gram,
            t_d_tags,
            t_d_body,
            t_def,
            t_def_line,
            t_word_name,
            t_word_origin,
        ) = style_tags

        gram_form = str(definition.slots or "") + (definition.grammar_code or "")
        def_gram = t_d_gram % gram_form if gram_form else ""
        def_tags = (
            t_d_tags % definition.case_tags.replace("-", "&zwj;-&zwj;")
            if definition.case_tags
            else ""
        )

        formatter = DefinitionFormatter(definition)
        def_body = formatter.tagged_definition_body(key, t_d_body)
        word_name = formatter.tagged_word_name(t_word_name)
        word_origin_x = formatter.tagged_word_origin_x(t_word_origin)

        inner_def = t_def % f"{def_tags}{def_gram}{def_body}"
        return t_def_line % f"{word_name}{word_origin_x}{inner_def}"
