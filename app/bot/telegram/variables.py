"""Telegram Bot variables for buttons and actions"""

# pylint: disable=C0103

t = "text"
cbd = "callback_data"

cancel = "cancel"
close = "close"


class Mark:
    language = "l"
    page = "p"
    action = "a"
    entity = "e"
    record_id = "r"
    slice_start = "s"


# entities
entity_predy = "ep"


# actions
class Action:
    send_card = "sc"
    kb_cpx_show = "cs"
    kb_cpx_hide = "ch"
    kb_afx_show = "as"
    kb_afx_hide = "ah"
    kb_pnt_show = "ps"
    kb_pnt_hide = "ph"
