from callbaker import callback_from_info
from keyboa import Keyboa

from app.bot.telegram import MIN_NUMBER_OF_BUTTONS
from app.bot.telegram.variables import (
    mark_entity,
    entity_predy,
    mark_action,
    mark_record_id,
    mark_slice_start,
    t,
    cbd,
    Action,
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
                    mark_action: Action.send_card,
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


def keyboard_show_hide(title: str, word_id: int, action_mark: str):
    """
    :return:
    """

    cbd_predy = {
        mark_entity: entity_predy,
        mark_action: action_mark,
        mark_record_id: word_id,
    }
    button = [
        {t: title, cbd: callback_from_info(cbd_predy)},
    ]
    return Keyboa(button)()


class WordKeyboard:

    def __init__(self, word):
        self.word = word
        self.items = self._get_items()

    def _get_items(self):
        if self.word.type.parentable:
            return self.word.parents
        return self.word.complexes

    def get_title(self, show: bool, items_type: str):
        show_text = "Show" if show else "Hide"

        match items_type:
            case "parent":
                return (
                    f"{show_text} Parent"
                    + f"{f's ({len(self.word.parents)})' if len(self.word.parents) > 1 else ''}"
                )
            case "djifoa":
                return (
                    f"{show_text} Djifoa"
                    + f"{f' ({len(self.word.affixes)})' if len(self.word.affixes) > 1 else ''}"
                )
            case "complex":
                return (
                    f"{show_text} Complex"
                    + f"{f'es ({len(self.word.complexes)})' if len(self.word.complexes) > 1 else ''}"
                )
            case _:
                return show_text

    def keyboard_cpx(self, action: str = "", slice_start: int = 0):
        """
        :param action:
        :param slice_start:
        :return:
        """
        print(action)

        match action:
            case Action.kb_cpx_show:
                title_djifoa = self.get_title(show=True, items_type="djifoa")
                kb_hide_djifoa = keyboard_show_hide(
                    title_djifoa, self.word.id, Action.kb_afx_hide
                )

                title_cpx = self.get_title(show=False, items_type="complex")
                kb_hide_cpx = keyboard_show_hide(
                    title_cpx, self.word.id, Action.kb_cpx_hide
                )
                kb_data = keyboard_data(slice_start, self.word.complexes)

                kb_navi = keyboard_navi(
                    slice_start,
                    len(self.word.complexes),
                    self.word.id,
                    Action.kb_cpx_show,
                )
                kb_combo = (kb_hide_djifoa, kb_hide_cpx, kb_data, kb_navi, kb_close())
                return Keyboa.combine(kb_combo)

            case Action.kb_cpx_hide:
                title_djifoa = self.get_title(show=True, items_type="djifoa")
                kb_hide_djifoa = keyboard_show_hide(
                    title_djifoa, self.word.id, Action.kb_afx_show
                )

                title_cpx = self.get_title(show=True, items_type="complex")
                kb_hide_cpx = keyboard_show_hide(
                    title_cpx, self.word.id, Action.kb_cpx_show
                )
                kb_combo = (kb_hide_djifoa, kb_hide_cpx, kb_close())
                return Keyboa.combine(kb_combo)

            case Action.kb_afx_show:
                title_djifoa = self.get_title(show=False, items_type="djifoa")
                kb_hide_djifoa = keyboard_show_hide(
                    title_djifoa, self.word.id, Action.kb_afx_hide
                )

                title_cpx = self.get_title(show=True, items_type="complex")
                kb_hide_cpx = keyboard_show_hide(
                    title_cpx, self.word.id, Action.kb_cpx_show
                )
                kb_data = keyboard_data(0, self.word.affixes)

                kb_combo = (kb_hide_djifoa, kb_data, kb_hide_cpx, kb_close())
                return Keyboa.combine(kb_combo)

            case Action.kb_afx_hide:
                print("apkah")
            case _:

                title_djifoa = self.get_title(show=True, items_type="djifoa")
                kb_hide_djifoa = keyboard_show_hide(
                    title_djifoa, self.word.id, Action.kb_afx_show
                )

                title_cpx = self.get_title(show=True, items_type="complex")
                kb_hide_cpx = keyboard_show_hide(
                    title_cpx, self.word.id, Action.kb_cpx_show
                )

                return Keyboa.combine((kb_hide_djifoa, kb_hide_cpx, kb_close()))
