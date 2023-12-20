# -*- coding: utf-8 -*-

from loglan_core.definition import BaseDefinition
from loglan_core.addons.definition_selector import DefinitionSelector
from loglan_core.event import BaseEvent
from loglan_core.word import BaseWord
from sqlalchemy.sql.selectable import Select

from app.site.compose import DEFAULT_HTML_STYLE, Item
from app.site.compose.definition_formatter import DefinitionFormatter


class EnglishItem(Item):
    def __init__(
        self,
        definitions: list[BaseDefinition],
        key: str,
        style: str = DEFAULT_HTML_STYLE,
    ):
        self.definitions = definitions
        self.key = key
        self.style = style

    @staticmethod
    def select_definitions_by_key(
        key: str,
        language: str = None,
        case_sensitive: bool = False,
        event_id: BaseEvent | int | str = None,
    ) -> Select:
        return (
            DefinitionSelector().by_key(
                key=key, language=language, case_sensitive=case_sensitive
            )
            .join(BaseWord)
            .filter(BaseWord.filter_by_event_id(event_id=event_id)).distinct(BaseWord.name)
            .order_by(BaseWord.name)
        )

    def export_as_html(self):
        return "\n".join(
            [self.export_for_english(d, self.key, self.style) for d in self.definitions]
        )

    @staticmethod
    def export_for_english(  # pylint: disable=too-many-locals
        definition: BaseDefinition,
        key: str,
        style: str = DEFAULT_HTML_STYLE,
    ) -> str:
        # de = definition english
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

        (
            t_d_gram,
            t_d_tags,
            t_d_body,
            t_def,
            t_def_line,
            t_word_name,
            t_word_origin,
        ) = tags[style]

        gram_form = str(definition.slots or "") + definition.grammar_code
        def_gram = t_d_gram % gram_form if gram_form else ""
        def_tags = (
            t_d_tags % definition.case_tags.replace("-", "&zwj;-&zwj;")
            if definition.case_tags
            else ""
        )

        def_body = DefinitionFormatter(definition).tagged_definition_body(key, t_d_body)
        word_name = DefinitionFormatter(definition).tagged_word_name(t_word_name)
        word_origin_x = DefinitionFormatter(definition).tagged_word_origin_x(
            t_word_origin
        )

        definition = t_def % f"{def_tags}{def_gram}{def_body}"
        return t_def_line % f"{word_name}{word_origin_x}{definition}"
