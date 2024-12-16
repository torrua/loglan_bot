from callbaker import callback_from_info
from keyboa import Keyboa

from app.bot.telegram import MIN_NUMBER_OF_BUTTONS
from app.bot.telegram.variables import (
    entity_predy,
    t,
    cbd,
    Action,
    Mark,
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
        Mark.entity: entity_predy,
        Mark.action: action_mark,
        Mark.record_id: word_id,
    }

    if index_start != 0:
        data_cbd_predy_kb_back = {
            **common_data,
            Mark.slice_start: index_start - delimiter,
        }
        button_back = {
            t: text_arrow_back,
            cbd: callback_from_info(data_cbd_predy_kb_back),
        }

    if index_end != number_of_items:
        data_cbd_predy_kb_forward = {
            **common_data,
            Mark.slice_start: index_end,
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
        Mark.entity: entity_predy,
        Mark.action: action_mark,
        Mark.record_id: word_id,
    }
    button = [
        {t: title, cbd: callback_from_info(cbd_predy)},
    ]
    return Keyboa(button)()


def combine_and_close(func):
    def wrapper(self, *args, **kwargs):
        kb_combo = func(self, *args, **kwargs)
        kbs = [i for i in kb_combo if i]
        kbs.append(kb_close())
        return Keyboa.combine(tuple(kbs))

    return wrapper


class WordKeyboard:

    def __init__(self, word):
        self.word = word

    def keyboard_data(self, action: str, slice_start: int = 0):
        """
        :param action:
        :param slice_start:
        :return:
        """
        items_dict = {
            "p": self.word.parents,
            "d": self.word.affixes,
            "c": self.word.complexes,
        }

        items = items_dict.get(action[0])
        if not items:
            return None

        slice_end = get_slice_end(slice_start, len(items))
        current_item_set = items[slice_start:slice_end]

        kb_items = [
            {
                t: item.name,
                cbd: callback_from_info(
                    {
                        Mark.entity: entity_predy,
                        Mark.action: Action.send_card,
                        Mark.record_id: item.id,
                    }
                ),
            }
            for item in current_item_set
        ]

        return Keyboa(items=kb_items, items_in_row=3)()

    def get_title(self, show: bool, items_type: str):
        show_text = "Show" if show else "Hide"

        title_formats = {
            "p": (
                f"{show_text} Parent ({len(self.word.parents)})"
                if len(self.word.parents) > 1
                else f"{show_text} Parent"
            ),
            "d": (
                f"{show_text} Djifoa ({len(self.word.affixes)})"
                if len(self.word.affixes)
                else f"{show_text} Djifoa"
            ),
            "c": (
                f"{show_text} Complex ({len(self.word.complexes)})"
                if len(self.word.complexes) > 1
                else f"{show_text} Complex"
            ),
        }

        return title_formats.get(items_type, show_text)

    def keyboard_show_hide(self, title: str, action_mark: str):
        """
        :return:
        """

        cbd_predy = {
            Mark.entity: entity_predy,
            Mark.action: action_mark,
            Mark.record_id: self.word.id,
        }
        button = [
            {t: title, cbd: callback_from_info(cbd_predy)},
        ]
        return Keyboa(button)()

    def get_title_kb(self, action: str):
        show = action.endswith("s")
        items_type = action[0]
        items = {
            "p": self.word.parents,
            "d": self.word.affixes,
            "c": self.word.complexes,
        }

        if not items.get(items_type):
            return None

        title = self.get_title(show, items_type)
        return keyboard_show_hide(title, self.word.id, action)

    def keyboard_cpx(self, action: str = "", slice_start: int = 0):
        """
        :param action:
        :param slice_start:
        :return:
        """

        match action:
            case Action.kb_cpx_show:
                return self.get_kb_cpx_show(slice_start)

            case Action.kb_dji_show:
                return self.get_kb_dji_show()

            case Action.kb_pnt_show:
                return self.get_kb_pnt_show()

            case _:
                return self.get_default_kb()

    @combine_and_close
    def get_kb_pnt_show(self):
        kb_title = self.get_title_kb(action=Action.kb_pnt_hide)
        kb_data = self.keyboard_data(action=Action.kb_pnt_hide)
        return [kb_title, kb_data]

    @combine_and_close
    def get_kb_cpx_show(self, slice_start: int = 0):
        kb_title_dji = self.get_title_kb(action=Action.kb_dji_show)
        kb_title_cpx = self.get_title_kb(action=Action.kb_cpx_hide)
        kb_data_cpx = self.keyboard_data(
            action=Action.kb_cpx_hide,
            slice_start=slice_start,
        )

        kb_navi = keyboard_navi(
            slice_start,
            len(self.word.complexes),
            self.word.id,
            Action.kb_cpx_show,
        )
        return [kb_title_dji, kb_title_cpx, kb_data_cpx, kb_navi]

    @combine_and_close
    def get_kb_dji_show(self):
        kb_title_dji = self.get_title_kb(action=Action.kb_dji_hide)
        kb_data = self.keyboard_data(action=Action.kb_dji_hide)
        kb_title_cpx = self.get_title_kb(action=Action.kb_cpx_show)
        return [kb_title_dji, kb_data, kb_title_cpx]

    @combine_and_close
    def get_default_kb(self):
        actions = [Action.kb_dji_show, Action.kb_cpx_show, Action.kb_pnt_show]
        return [self.get_title_kb(action=action) for action in actions]
