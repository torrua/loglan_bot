# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from typing import List

from callbaker import callback_from_info
from keyboa import Keyboa
from loglan_db.model_db.base_word import BaseWord
from loglan_db.model_db.base_definition import BaseDefinition
from loglan_db.model_db.addons.addon_word_getter import AddonWordGetter
from variables import (
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


class TelegramDefinition(BaseDefinition):
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

    @classmethod
    def translation_by_key(cls, request: str, language: str = None) -> str:
        """
        We get information about loglan words by key in a foreign language
        :param request: Requested string
        :param language: Key language
        :return: Search results string formatted for sending to Telegram
        """
        result = {}

        for definition in cls.by_key(request, language).all():
            source_word_name = definition.source_word.name
            if not result.get(source_word_name):
                result[source_word_name] = []
            result[source_word_name].append(definition.export())

        result = dict(sorted(result.items()))
        new = "\n"
        return new.join(
            [
                f"/{word_name},\n{new.join(definitions)}\n"
                for word_name, definitions in result.items()
            ]
        ).strip()


class TelegramWord(BaseWord, AddonWordGetter):
    """Word class extensions for Telegram"""

    def export(self) -> str:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """

        w_match = self.match + " " if self.match else ""
        w_year = "'" + str(self.year.year)[-2:] + " "
        w_authors = "/".join([a.abbreviation for a in self.authors]) + " "
        w_type = self.type.type + " "
        w_rank = self.rank + " " if self.rank else ""
        word_str = (
            f"<b>{self.name}</b>{self._w_affixes},"
            f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{self._w_orig}"
        )

        return f"{word_str}\n\n{self._exported_definitions_as_string}"

    @property
    def _exported_definitions_as_string(self):
        return "\n\n".join([d.export() for d in self.get_definitions()])

    @property
    def _w_orig(self) -> str:
        w_origin_x = " = " + self.origin_x if self.origin_x else ""
        return (
            "\n<i>&#60;" + self.origin + w_origin_x + "&#62;</i>"
            if self.origin or w_origin_x
            else ""
        )

    @property
    def _w_affixes(self) -> str:
        list_of_afx = ["" + w.name for w in self.affixes]
        w_affixes = f" ({' '.join(list_of_afx)})" if list_of_afx else ""
        return w_affixes

    def get_definitions(self) -> List[TelegramDefinition]:
        """
        Get all definitions of the word
        :return: List of Definition objects ordered by Definition.position
        """
        return (
            TelegramDefinition.query.filter(BaseDefinition.word_id == self.id)
            .order_by(BaseDefinition.position.asc())
            .all()
        )

    def send_card_to_user(self, bot, user_id, parse_mode):
        """

        :param bot:
        :param user_id:
        :param parse_mode:
        :return:
        """
        bot.send_message(
            chat_id=user_id,
            text=self.export(),
            parse_mode=parse_mode,
            reply_markup=self.keyboard_cpx(),
        )

    @classmethod
    def by_request(cls, request) -> list:
        """

        :param request:
        :return:
        """

        return (
            [
                cls.get_by_id(request),
            ]
            if isinstance(request, int)
            else cls.by_name(request).all()
        )

    def keyboard_cpx(self, show_list: bool = False, slice_start: int = 0):
        """

        :param show_list:
        :param slice_start:
        :return:
        """
        return TelegramWordKeyboard(self).keyboard_cpx(
            show_list=show_list, slice_start=slice_start
        )


class TelegramWordKeyboard:
    """
    Keyboard for telegram bot
    """

    word = None

    def __init__(self, word: TelegramWord):
        self.word = word

    def keyboard_navi(self, index_start, total_num_of_cpx):
        """

        :param index_start:
        :param total_num_of_cpx:
        :return:
        """
        delimiter = self.get_delimiter(total_num_of_cpx)
        index_end = self.get_slice_end(index_start, total_num_of_cpx)

        if total_num_of_cpx <= delimiter:
            return None

        common_data = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show,
            mark_record_id: self.word.id,
        }

        nav_row = []

        if index_start != 0:
            text_arrow_back = "\U0000276E" * 2

            cbd_predy_kb_cpx_back = {
                **common_data,
                mark_slice_start: index_start - delimiter,
            }
            button_back = {
                t: text_arrow_back,
                cbd: callback_from_info(cbd_predy_kb_cpx_back),
            }
            nav_row.append(button_back)

        if index_end != len(self.word.complexes.all()):
            text_arrow_forward = "\U0000276F" * 2

            cbd_predy_kb_cpx_forward = {
                **common_data,
                mark_slice_start: index_end,
            }
            button_forward = {
                t: text_arrow_forward,
                cbd: callback_from_info(cbd_predy_kb_cpx_forward),
            }
            nav_row.append(button_forward)

        return Keyboa(nav_row, items_in_row=2)()

    def keyboard_cpx_switcher(self, total_number_of_complexes: int, show: bool = True):
        """

        :param total_number_of_complexes:
        :param show:
        :return:
        """
        button_text_number = f"({total_number_of_complexes})" if show else ""
        _es = (
            f"es {button_text_number}".strip() if total_number_of_complexes > 1 else ""
        )
        button_text_action = "Show" if show else "Hide"
        text = f"{button_text_action} Complex{_es}"

        callback_data = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show if show else action_predy_kb_cpx_hide,
            mark_record_id: self.word.id,
        }
        buttons = [
            {t: text, cbd: callback_from_info(callback_data)},
        ]
        return Keyboa(buttons)()

    @staticmethod
    def get_delimiter(total_number_of_complexes: int):
        """

        :param total_number_of_complexes:
        :return:
        """
        from bot import MIN_NUMBER_OF_BUTTONS

        allowed_range = list(range(MIN_NUMBER_OF_BUTTONS, MIN_NUMBER_OF_BUTTONS + 11))
        lst = [(total_number_of_complexes % i, i) for i in allowed_range]
        delimiter = min(lst, key=lambda x: abs(x[0] - MIN_NUMBER_OF_BUTTONS))[1]
        for i in lst:
            if i[0] == 0:
                delimiter = i[1]
                break
        return delimiter

    @staticmethod
    def keyboard_data(current_complexes):
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

    @property
    def kb_cpx_close(self):
        """

        :return:
        """
        return Keyboa({t: "Close", cbd: "close"})()

    def keyboard_cpx(self, show_list: bool = False, slice_start: int = 0):
        """

        :param show_list:
        :param slice_start:
        :return:
        """

        total_num_of_cpx = self.word.complexes.count()

        if not total_num_of_cpx:
            return self.kb_cpx_close

        if not show_list:
            keyboards = (
                self.keyboard_cpx_switcher(total_num_of_cpx, show=True),
                self.kb_cpx_close,
            )
            return Keyboa.combine(keyboards)

        slice_end = self.get_slice_end(slice_start, total_num_of_cpx)

        current_cpx_set = self.word.complexes.all()[slice_start:slice_end]
        kb_cpx_data = self.keyboard_data(current_cpx_set)

        kb_cpx_nav = self.keyboard_navi(slice_start, total_num_of_cpx)
        kb_cpx_hide = self.keyboard_cpx_switcher(total_num_of_cpx, show=False)

        kb_combo = (kb_cpx_hide, kb_cpx_data, kb_cpx_nav, self.kb_cpx_close)
        return Keyboa.combine(kb_combo)

    def get_slice_end(self, slice_start, total_num_of_cpx):
        """

        :param slice_start:
        :param total_num_of_cpx:
        :return:
        """
        current_delimiter = self.get_delimiter(total_num_of_cpx)
        last_allowed_element = slice_start + current_delimiter
        slice_end = (
            last_allowed_element
            if last_allowed_element < total_num_of_cpx
            else total_num_of_cpx
        )
        return slice_end
