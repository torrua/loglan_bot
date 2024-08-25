# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from collections import defaultdict

from callbaker import callback_from_info
from keyboa import Keyboa
from loglan_core.addons.definition_selector import DefinitionSelector
from loglan_core.addons.word_selector import WordSelector
from loglan_core import Word, Definition

from app.bot.telegram import MIN_NUMBER_OF_BUTTONS
from app.bot.telegram.variables import (
    t,
    cbd,
    mark_action,
    mark_entity,
    mark_record_id,
    mark_slice_start,
    action_predy_send_card,
    entity_predy,
    action_predy_kb_cpx_show,
    action_predy_kb_cpx_hide,
)


class TelegramDefinition(Definition):
    """Definition class extensions for Telegram"""

    def export(self):
        """
        Convert definition's data to str for sending as a telegram messages
        :return: Adopted for posting in telegram string
        """
        d_usage = f"<b>{self.usage.replace('%', '—')}</b> " if self.usage else ""
        d_grammar = (
            f"({self.slots if self.slots is not None else ''}{self.grammar_code}) "
        )
        d_body = (
            self.body.replace("<", "&#60;")
            .replace(">", "&#62;")
            .replace("«", "<i>")
            .replace("»", "</i>")
            .replace("{", "<code>")
            .replace("}", "</code>")
            .replace("....", "….")
            .replace("...", "…")
        )

        d_case_tags = f" [{self.case_tags}]" if self.case_tags else ""
        return f"{d_usage}{d_grammar}{d_body}{d_case_tags}"


class TelegramWord(Word):
    """Word class extensions for Telegram"""

    def format_affixes(self):
        return (
            f" ({' '.join([w.name for w in self.affixes]).strip()})"
            if self.affixes
            else ""
        )

    def format_year(self):
        return "'" + str(self.year.year)[-2:] + " " if self.year else ""

    def format_origin(self):
        if self.origin or self.origin_x:
            return (
                f"\n<i>&#60;{self.origin}"
                f"{' = ' + self.origin_x if self.origin_x else ''}&#62;</i>"
            )
        return ""

    def format_authors(self):
        return (
            "/".join([a.abbreviation for a in self.authors]) + " "
            if self.authors
            else ""
        )

    def format_rank(self):
        return self.rank + " " if self.rank else ""

    def export_as_str(self, session) -> str:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """
        w_affixes = self.format_affixes()
        w_match = self.match + " " if self.match else ""
        w_year = self.format_year()
        w_orig = self.format_origin()
        w_authors = self.format_authors()
        w_type = self.type.type + " "
        w_rank = self.format_rank()

        word_str = (
            f"<b>{self.name}</b>{w_affixes},"
            f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"
        )
        return f"{word_str}\n\n{self.get_definitions(session=session)}"

    def get_definitions(self, session) -> str:
        """
        Get all definitions of the word
        :param session: Session
        :return: List of Definition objects ordered by position
        """

        definitions = (
            DefinitionSelector(class_=TelegramDefinition)
            .filter(TelegramDefinition.word_id == self.id)
            .order_by(TelegramDefinition.position.asc())
            .all(session=session)
        )

        return "\n\n".join([d.export() for d in definitions])

    @classmethod
    def translation_by_key(cls, session, request: str, language: str = None) -> str:
        """
        We get information about loglan words by key in a foreign language
        :param session: Session
        :param request: Requested string
        :param language: Key language
        :return: Search results string formatted for sending to Telegram
        """

        result = defaultdict(list)
        definitions = (
            DefinitionSelector(class_=TelegramDefinition)
            .by_key(key=request, language=language)
            .all(session=session)
        )

        for definition in definitions:
            result[definition.source_word.name].append(definition.export())

        new = "\n"
        word_items = [
            f"/{word_name},\n{new.join(definitions)}\n"
            for word_name, definitions in result.items()
        ]
        return new.join(word_items).strip()

    def _keyboard_navi(self, index_start: int, index_end: int, delimiter: int):
        """
        :param index_start:
        :param index_end:
        :param delimiter:
        :return:
        """
        text_arrow_back = "\U0000276E" * 2
        text_arrow_forward = "\U0000276F" * 2
        button_back, button_forward = None, None

        common_data = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show,
            mark_record_id: self.id,
        }
        if index_start != 0:
            cbd_predy_kb_cpx_back = {
                **common_data,
                mark_slice_start: index_start - delimiter,
            }
            button_back = {
                t: text_arrow_back,
                cbd: callback_from_info(cbd_predy_kb_cpx_back),
            }

        if index_end != len(self.complexes):
            cbd_predy_kb_cpx_forward = {
                **common_data,
                mark_slice_start: index_end,
            }
            button_forward = {
                t: text_arrow_forward,
                cbd: callback_from_info(cbd_predy_kb_cpx_forward),
            }

        nav_row = [b for b in [button_back, button_forward] if b]
        return Keyboa(nav_row, items_in_row=2)()

    def _keyboard_hide(self, total_number_of_complexes: int):
        """
        :param total_number_of_complexes:
        :return:
        """
        text_cpx_hide = f"Hide Complex{'es' if total_number_of_complexes > 1 else ''}"
        cbd_predy_kb_cpx_hide = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_hide,
            mark_record_id: self.id,
        }
        button_predy_kb_cpx_hide = [
            {t: text_cpx_hide, cbd: callback_from_info(cbd_predy_kb_cpx_hide)},
        ]
        return Keyboa(button_predy_kb_cpx_hide)()

    def _keyboard_show(self, total_number_of_complexes: int):
        """
        :param total_number_of_complexes:
        :return:
        """
        text_cpx_show = (
            f"Show Complex{'es' if total_number_of_complexes > 1 else ''}"
            f" ({total_number_of_complexes})"
        )
        cbd_predy_kb_cpx_show = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show,
            mark_record_id: self.id,
        }
        button_show = [
            {t: text_cpx_show, cbd: callback_from_info(cbd_predy_kb_cpx_show)},
        ]
        return Keyboa.combine((Keyboa(button_show)(), kb_close()))

    @staticmethod
    def _get_delimiter(total_number_of_complexes: int):
        """
        :param total_number_of_complexes:
        :return:
        """
        allowed_range = list(range(MIN_NUMBER_OF_BUTTONS, MIN_NUMBER_OF_BUTTONS + 11))
        lst = [(total_number_of_complexes % i, i) for i in allowed_range]
        delimiter = min(lst, key=lambda x: abs(x[0] - MIN_NUMBER_OF_BUTTONS))[1]
        for i in lst:
            if i[0] == 0:
                delimiter = i[1]
                break
        return delimiter

    @staticmethod
    def _keyboard_data(current_complexes: list):
        """
        :param current_complexes:
        :return:
        """
        cpx_items = [
            {
                t: cpx.name,
                cbd: callback_from_info(
                    {
                        mark_entity: entity_predy,
                        mark_action: action_predy_send_card,
                        mark_record_id: cpx.id,
                    }
                ),
            }
            for cpx in current_complexes
        ]
        return Keyboa(items=cpx_items, alignment=True, items_in_row=4)()

    def keyboard_cpx(self, show_list: bool = False, slice_start: int = 0):
        """
        :param show_list:
        :param slice_start:
        :return:
        """

        total_num_of_cpx = len(self.complexes)

        if not total_num_of_cpx:
            return kb_close()

        if not show_list:
            return self._keyboard_show(total_num_of_cpx)

        current_delimiter = self._get_delimiter(total_num_of_cpx)

        kb_cpx_hide = self._keyboard_hide(total_num_of_cpx)

        last_allowed_item = slice_start + current_delimiter
        slice_end = min(last_allowed_item, total_num_of_cpx)

        current_cpx_set = self.complexes[slice_start:slice_end]
        kb_cpx_data = self._keyboard_data(current_cpx_set)

        kb_cpx_nav = None

        if total_num_of_cpx > current_delimiter:
            kb_cpx_nav = self._keyboard_navi(slice_start, slice_end, current_delimiter)

        kb_combo = (kb_cpx_hide, kb_cpx_data, kb_cpx_nav, kb_close())

        return Keyboa.combine(kb_combo)

    async def send_card_to_user(self, session, bot, user_id: int | str):
        """
        :param session:
        :param bot:
        :param user_id:
        :return:
        """
        await bot.send_message(
            chat_id=user_id,
            text=self.export_as_str(session),
            reply_markup=self.keyboard_cpx(),
        )

    @classmethod
    def by_request(cls, session, request: str) -> list:
        """
        :param session:
        :param request:
        :return:
        """
        if isinstance(request, int):
            return [
                cls.get_by_id(session, request),
            ]
        return WordSelector(TelegramWord).by_name(request).all(session)


def kb_close():
    """
    :return:
    """
    return Keyboa({t: "Close", cbd: "close"})()
