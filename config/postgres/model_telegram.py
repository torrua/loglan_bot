# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from typing import List, Optional
from config.postgres.model_base import BaseDefinition, BaseWord
from callbaker import callback_from_info
from variables import t, cbd, \
    mark_action, mark_entity, mark_record_id, \
    action_predy_send_card, entity_predy, action_predy_kb_cpx_show, action_predy_kb_cpx_hide
from keyboa.keyboards import MAXIMUM_ITEMS_IN_LINE


class TelegramDefinition(BaseDefinition):
    """Definition class extensions for Telegram"""

    def export(self):
        """
        Convert definition's data to str for sending as a telegram messages
        :return: Adopted for posting in telegram string
        """
        d_usage = f"<b>{self.usage.replace('%', '—')}</b> " if self.usage else ""
        d_grammar = f"({self.slots if self.slots is not None else ''}{self.grammar_code}) "
        d_body = self.body \
            .replace('<', '&#60;').replace('>', '&#62;') \
            .replace('«', '<i>').replace('»', '</i>') \
            .replace('≤', '<code>').replace('≥', '</code>')

        d_case_tags = f" [{self.case_tags}]" if self.case_tags else ""
        return f"{d_usage}{d_grammar}{d_body}{d_case_tags}"


class TelegramWord(BaseWord):
    """Word class extensions for Telegram"""

    def export(self) -> str:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """

        def split_list(a_list):
            half = len(a_list) // 2
            return [a_list[:half], a_list[half:]]

        # Word
        list_of_afx = ["" + w.name for w in self.affixes]
        w_affixes = f" ({' '.join(list_of_afx)})" if list_of_afx else ""
        w_match = self.match + " " if self.match else ""
        w_year = "'" + str(self.year.year)[-2:] + " "
        w_origin_x = " = " + self.origin_x if self.origin_x else ""
        w_orig = "\n<i>&#60;" + self.origin + w_origin_x + "&#62;</i>" \
            if self.origin or w_origin_x else ""
        w_authors = '/'.join([a.abbreviation for a in self.authors]) + " "
        w_type = self.type.type + " "
        w_rank = self.rank + " " if self.rank else ""
        word_str = f"<b>{self.name}</b>{w_affixes}," \
                   f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"

        # Definitions TODO maybe extract from method
        definitions_str = "\n\n".join([d.export() for d in self.get_definitions()])

        # Used in
        list_of_all_cpx = ["/" + w.name for w in self.complexes]

        # Divide the list if the text does not place in one message
        split_cpx = split_list(list_of_all_cpx) if \
            len("; ".join(list_of_all_cpx)) > 3900 else [list_of_all_cpx, ]

        """
        used_in_str = ["\n\nUsed in: " + "; ".join(list_cpx)
                       if list_cpx else "" for list_cpx in split_cpx]
        """

        return f"{word_str}\n\n{definitions_str}"

    def get_definitions(self) -> List[TelegramDefinition]:
        """
        Get all definitions of the word
        :return: List of Definition objects ordered by Definition.position
        """
        return TelegramDefinition.query.filter(BaseDefinition.word_id == self.id)\
            .order_by(BaseDefinition.position.asc()).all()

    @classmethod
    def translation_by_key(cls, request: str, language: str = None) -> str:
        """
        We get information about loglan words by key in a foreign language
        :param request: Requested string
        :param language: Key language
        :return: Search results string formatted for sending to Telegram
        """
        words = cls.by_key(request, language).order_by(cls.name).all()
        result = {}

        for word in words:
            result[word.name] = []
            for definition in word.get_definitions():
                keys = [key.word.lower() for key in definition.keys]
                if request.lower() in keys:
                    result[word.name].append(definition.export())

        new = '\n'

        return new.join([f"/{word_name},{new}{new.join(definitions)}{new}"
                         for word_name, definitions in result.items()]).strip()

    def keyboard_cpx(self, show_list: bool = False) -> Optional[List[List[dict]]]:
        """

        :return:
        """
        # TODO Add scrolling if number of cpx more than 100

        complexes = self.complexes

        if not complexes:
            return None

        if not show_list:
            callback_data_predy_kb_cpx_show = {
                mark_entity: entity_predy,
                mark_action: action_predy_kb_cpx_show,
                mark_record_id: self.id, }

            button_show = [{
                t: f"Show Complex{'es' if len(complexes) > 1 else ''} ({len(complexes)})",
                cbd: callback_from_info(callback_data_predy_kb_cpx_show)}, ]
            button_close = [{t: "Close", cbd: "close"}, ]
            return [button_show, button_close, ]

        callback_data_predy_kb_cpx_hide = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_hide,
            mark_record_id: self.id, }
        button = [{
            t: f"Hide Complex{'es' if len(complexes) > 1 else ''}",
            cbd: callback_from_info(callback_data_predy_kb_cpx_hide)}, ]
        cpx_buttons = [button, ]

        len_current_row = 0
        current_row = []

        complexes_names = [c.name for c in complexes]
        total_avg = sum(map(len, complexes_names)) / len(complexes_names)
        average_items_in_line = 4
        max_len_row = total_avg * average_items_in_line + average_items_in_line

        for cpx in complexes:

            callback_data = {
                mark_entity: entity_predy,
                mark_action: action_predy_send_card,
                mark_record_id: cpx.id, }

            button = {t: cpx.name, cbd: callback_from_info(callback_data)}

            if len_current_row + len(cpx.name) < max_len_row \
                    and len(current_row) < MAXIMUM_ITEMS_IN_LINE:
                current_row.append(button)
                len_current_row = len_current_row + len(cpx.name)
            else:
                cpx_buttons.append(current_row)
                len_current_row = len(cpx.name)
                current_row = [button, ]

        if current_row:
            cpx_buttons.append(current_row)

        cpx_buttons.append([{t: "Close", cbd: "close"}, ])
        return cpx_buttons
