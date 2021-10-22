# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from typing import List

from callbaker import callback_from_info
from keyboa import Keyboa
from config import log
from loglan_db.model_db.base_word import BaseWord
from loglan_db.model_db.base_definition import BaseDefinition
from loglan_db.model_db.addons.addon_word_getter import AddonWordGetter
from variables import t, cbd, \
    mark_action, mark_entity, mark_record_id, mark_slice_start, \
    action_predy_send_card, entity_predy, action_predy_kb_cpx_show, action_predy_kb_cpx_hide


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
            .replace('{', '<code>').replace('}', '</code>') \
            .replace('....', '….').replace('...', '…')

        d_case_tags = f" [{self.case_tags}]" if self.case_tags else ""
        return f"{d_usage}{d_grammar}{d_body}{d_case_tags}"


class TelegramWord(BaseWord, AddonWordGetter):
    """Word class extensions for Telegram"""

    def export(self) -> str:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """

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

        return new.join([f"/{word_name},\n{new.join(definitions)}\n"
                         for word_name, definitions in result.items()]).strip()

    def keyboard_cpx(self, show_list: bool = False, slice_start: int = 0):
        """

        :return:
        """

        kb_cpx_close = Keyboa({t: "Close", cbd: "close"})()

        def keyboard_navi(index_start, index_end, delimiter):

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
                    **common_data, mark_slice_start: index_start - delimiter, }
                button_back = {
                    t: text_arrow_back,
                    cbd: callback_from_info(cbd_predy_kb_cpx_back)}

            if index_end != len(self.complexes.all()):
                cbd_predy_kb_cpx_forward = {
                    **common_data, mark_slice_start: index_end, }
                button_forward = {
                    t: text_arrow_forward,
                    cbd: callback_from_info(cbd_predy_kb_cpx_forward)}

            nav_row = [b for b in [button_back, button_forward] if b]
            return Keyboa(nav_row, items_in_row=2)()

        def keyboard_data(current_complexes):
            cpx_items = [{t: cpx.name, cbd: callback_from_info({
                mark_entity: entity_predy,
                mark_action: action_predy_send_card,
                mark_record_id: cpx.id, })} for cpx in current_complexes]
            return Keyboa(items=cpx_items, alignment=True, items_in_row=4)()

        def keyboard_hide(total_number_of_complexes):
            text_cpx_hide = f"Hide Complex{'es' if total_number_of_complexes > 1 else ''}"
            cbd_predy_kb_cpx_hide = {
                mark_entity: entity_predy,
                mark_action: action_predy_kb_cpx_hide,
                mark_record_id: self.id, }
            button_predy_kb_cpx_hide = [{
                t: text_cpx_hide, cbd: callback_from_info(cbd_predy_kb_cpx_hide)}, ]
            return Keyboa(button_predy_kb_cpx_hide)()

        def keyboard_show(total_number_of_complexes: int):
            log.debug("tot_num_cpx: %s", total_number_of_complexes)
            text_cpx_show = f"Show Complex{'es' if total_number_of_complexes > 1 else ''} ({total_number_of_complexes})"
            cbd_predy_kb_cpx_show = {
                mark_entity: entity_predy,
                mark_action: action_predy_kb_cpx_show,
                mark_record_id: self.id, }
            button_show = [{
                t: text_cpx_show, cbd: callback_from_info(cbd_predy_kb_cpx_show)}, ]
            return Keyboa.combine((Keyboa(button_show)(), kb_cpx_close))

        def get_delimiter(total_number_of_complexes: int):
            from bot import MIN_NUMBER_OF_BUTTONS
            allowed_range = list(range(MIN_NUMBER_OF_BUTTONS, MIN_NUMBER_OF_BUTTONS + 11))
            lst = [(total_number_of_complexes % i, i) for i in allowed_range]
            delimiter = min(lst, key=lambda x: abs(x[0] - MIN_NUMBER_OF_BUTTONS))[1]
            for i in lst:
                if i[0] == 0:
                    delimiter = i[1]
                    break
            return delimiter

        total_num_of_cpx = self.complexes.count()

        if not total_num_of_cpx:
            return kb_cpx_close

        if not show_list:
            return keyboard_show(total_num_of_cpx)

        current_delimiter = get_delimiter(total_num_of_cpx)

        kb_cpx_hide = keyboard_hide(total_num_of_cpx)

        last_allowed_element = slice_start + current_delimiter
        slice_end = last_allowed_element if last_allowed_element < total_num_of_cpx else total_num_of_cpx

        current_cpx_set = self.complexes.all()[slice_start:slice_end]
        kb_cpx_data = keyboard_data(current_cpx_set)

        kb_cpx_nav = None

        if total_num_of_cpx > current_delimiter:
            kb_cpx_nav = keyboard_navi(slice_start, slice_end, current_delimiter)

        kb_combo = (kb_cpx_hide, kb_cpx_data, kb_cpx_nav, kb_cpx_close)

        return Keyboa.combine(kb_combo)

    def send_card_to_user(self, bot, user_id, parse_mode):
        bot.send_message(
            chat_id=user_id,
            text=self.export(),
            parse_mode=parse_mode,
            reply_markup=self.keyboard_cpx())
