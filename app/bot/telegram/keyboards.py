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


def get_delimiter(number_of_items: int) -> int:

    allowed_range = list(range(MIN_NUMBER_OF_BUTTONS, MIN_NUMBER_OF_BUTTONS + 11))
    lst = [(number_of_items % i, i) for i in allowed_range]
    delimiter = min(lst, key=lambda x: abs(x[0] - MIN_NUMBER_OF_BUTTONS))[1]
    for i in lst:
        if i[0] == 0:
            delimiter = i[1]
            break
    return delimiter


def get_slice_end(slice_start: int, number_of_items: int) -> int:
    last_allowed_item = slice_start + get_delimiter(number_of_items)
    slice_end = min(last_allowed_item, number_of_items)
    return slice_end


def keyboard_data(slice_start: int, items: list):
    """
    :param items:
    :param slice_start:
    :return:
    """
    slice_end = get_slice_end(slice_start, len(items))
    current_item_set = items[slice_start:slice_end]

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
        for item in current_item_set
    ]
    return Keyboa(items=kb_items, items_in_row=3)()


def keyboard_navi(
    index_start: int, number_of_items: int, word_id: int, action_mark: str
):
    """
    :param action_mark:
    :param word_id:
    :param number_of_items:
    :param index_start:
    :return:
    """

    delimiter = get_delimiter(number_of_items)
    if number_of_items <= delimiter:
        return None

    index_end = get_slice_end(index_start, number_of_items)

    text_arrow_back = "❮❮"
    text_arrow_forward = "❯❯"
    button_back, button_forward = None, None

    common_data = {
        mark_entity: entity_predy,
        mark_action: action_mark,
        mark_record_id: word_id,
    }

    if index_start != 0:
        data_cbd_predy_kb_back = {
            **common_data,
            mark_slice_start: index_start - delimiter,
        }
        button_back = {
            t: text_arrow_back,
            cbd: callback_from_info(data_cbd_predy_kb_back),
        }

    if index_end != number_of_items:
        data_cbd_predy_kb_forward = {
            **common_data,
            mark_slice_start: index_end,
        }
        button_forward = {
            t: text_arrow_forward,
            cbd: callback_from_info(data_cbd_predy_kb_forward),
        }

    nav_row = [b for b in [button_back, button_forward] if b]
    return Keyboa(nav_row, items_in_row=2)()


def kb_close():
    """
    :return:
    """
    return Keyboa({t: "Close", cbd: "close"})()


class WordKeyboard:

    def __init__(self, word):
        self.word = word
        self.items = self._get_items()

    def _get_items(self):
        if self.word.type.parentable:
            return self.word.parents
        return self.word.complexes

    def get_title(self):
        if self.word.type.parentable:
            return "Parent" + f"{'s' if len(self.word.parents) > 1 else ''}"
        return "Complex" + f"{'es' if len(self.word.complexes) > 1 else ''}"

    def _keyboard_hide(self):
        """
        :return:
        """

        text_hide = f"Hide {self.get_title()}"
        cbd_predy_kb_cpx_hide = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_hide,
            mark_record_id: self.word.id,
        }
        button_predy_kb_cpx_hide = [
            {t: text_hide, cbd: callback_from_info(cbd_predy_kb_cpx_hide)},
        ]
        return Keyboa(button_predy_kb_cpx_hide)()

    def _keyboard_show(self):
        """
        :return:
        """
        total_num = len(self.items)
        number = f" ({total_num})" if total_num > 1 else ""
        text_cpx_show = f"Show {self.get_title()}{number}"
        cbd_predy_kb_cpx_show = {
            mark_entity: entity_predy,
            mark_action: action_predy_kb_cpx_show,
            mark_record_id: self.word.id,
        }
        button_show = [
            {t: text_cpx_show, cbd: callback_from_info(cbd_predy_kb_cpx_show)},
        ]
        return Keyboa.combine((Keyboa(button_show)(), kb_close()))

    def _keyboard_complete(self, slice_start: int, items: list, word_id: int):
        kb_data = keyboard_data(slice_start, items)
        kb_navi = keyboard_navi(
            slice_start, len(items), word_id, action_predy_kb_cpx_show
        )
        kb_hide = self._keyboard_hide()
        kb_combo = (kb_hide, kb_data, kb_navi, kb_close())
        return Keyboa.combine(kb_combo)

    def keyboard_cpx(self, show_list: bool = False, slice_start: int = 0):
        """
        :param show_list:
        :param slice_start:
        :return:
        """

        if not self.items:
            return kb_close()

        if not show_list:
            return self._keyboard_show()

        return self._keyboard_complete(slice_start, self.items, self.word.id)
