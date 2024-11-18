from callbaker import callback_from_info
from keyboa import Keyboa

from app.bot.telegram import MIN_NUMBER_OF_BUTTONS
from app.bot.telegram.variables import (
    mark_entity,
    entity_predy,
    mark_action,
    action_predy_kb_cpx_show,
    mark_record_id,
    mark_slice_start,
    t,
    cbd,
    action_predy_kb_cpx_hide,
    action_predy_send_card,
)


class WordKeyboard:
    def __init__(self, word):
        self.word = word

    def _keyboard_navi(self, index_start: int, total_num: int):
        """
        :param index_start:
        :return:
        """

        delimiter = self._get_delimiter(total_num)
        if total_num <= delimiter:
            return None

        index_end = self.get_slice_end(index_start, total_num)

        text_arrow_back = "\U0000276E" * 2
        text_arrow_forward = "\U0000276F" * 2
        button_back, button_forward = None, None

        common_data = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show,
            mark_record_id: self.word.id,
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

        if index_end != len(self.word.complexes):
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
            mark_record_id: self.word.id,
        }
        button_predy_kb_cpx_hide = [
            {t: text_cpx_hide, cbd: callback_from_info(cbd_predy_kb_cpx_hide)},
        ]
        return Keyboa(button_predy_kb_cpx_hide)()

    def _keyboard_show(self, total_number_of_items: int):
        """
        :param total_number_of_items:
        :return:
        """
        text_cpx_show = (
            f"Show Complex{'es' if total_number_of_items > 1 else ''}"
            f" ({total_number_of_items})"
        )
        cbd_predy_kb_cpx_show = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show,
            mark_record_id: self.word.id,
        }
        button_show = [
            {t: text_cpx_show, cbd: callback_from_info(cbd_predy_kb_cpx_show)},
        ]
        return Keyboa.combine((Keyboa(button_show)(), kb_close()))

    @staticmethod
    def _get_delimiter(total_number_of_items: int):
        """
        :param total_number_of_items:
        :return:
        """
        allowed_range = list(range(MIN_NUMBER_OF_BUTTONS, MIN_NUMBER_OF_BUTTONS + 11))
        lst = [(total_number_of_items % i, i) for i in allowed_range]
        delimiter = min(lst, key=lambda x: abs(x[0] - MIN_NUMBER_OF_BUTTONS))[1]
        for i in lst:
            if i[0] == 0:
                delimiter = i[1]
                break
        return delimiter

    @staticmethod
    def _keyboard_data(items: list):
        """
        :param items:
        :return:
        """
        kb_items = [
            {
                t: item.name,
                cbd: callback_from_info(
                    {
                        mark_entity: entity_predy,
                        mark_action: action_predy_send_card,
                        mark_record_id: item.id,
                    }
                ),
            }
            for item in items
        ]
        return Keyboa(items=kb_items, alignment=True, items_in_row=4)()

    def keyboard_cpx(self, show_list: bool = False, slice_start: int = 0):
        """
        :param show_list:
        :param slice_start:
        :return:
        """

        all_items = self.word.complexes

        total_num = len(all_items)

        if not total_num:
            return kb_close()

        if not show_list:
            return self._keyboard_show(total_num)

        slice_end = self.get_slice_end(slice_start, total_num)
        current_item_set = all_items[slice_start:slice_end]

        kb_cpx_data = self._keyboard_data(current_item_set)

        kb_cpx_nav = self._keyboard_navi(slice_start, total_num)
        kb_cpx_hide = self._keyboard_hide(total_num)

        kb_combo = (kb_cpx_hide, kb_cpx_data, kb_cpx_nav, kb_close())

        return Keyboa.combine(kb_combo)

    def get_slice_end(self, slice_start, total_num):
        current_delimiter = self._get_delimiter(total_num)
        last_allowed_item = slice_start + current_delimiter
        slice_end = min(last_allowed_item, total_num)
        return slice_end


def kb_close():
    """
    :return:
    """
    return Keyboa({t: "Close", cbd: "close"})()
