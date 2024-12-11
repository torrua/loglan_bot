"""Processing inline buttons calls received from telegram bot"""

from callbaker import info_from_callback
from loglan_core import WordSelector

from app.bot.telegram import bot, cbq
from app.bot.telegram.keyboards import WordKeyboard
from app.bot.telegram.models import export_as_str
from app.bot.telegram.variables import mark_record_id, mark_slice_start, mark_action
from app.decorators import logging_time
from app.engine import async_session_maker


@logging_time
async def bib_cancel(call: cbq):
    """
    Обработка нажатия кнопки 'Отмена'
    :param call:
    :return:
    """
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@logging_time
async def bib_predy_send_card(call: cbq):
    """
    Обработка нажатия кнопки со logpua
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    uid = call.message.chat.id

    async with async_session_maker() as session:
        word = await (
            WordSelector()
            .filter_by(id=info[mark_record_id])
            .with_relationships()
            .scalar_async(session)
        )
        await bot.send_message(
            chat_id=uid,
            text=export_as_str(word),
            reply_markup=WordKeyboard(word).keyboard_cpx(),
        )


@logging_time
async def bib_predy_kb_cpx_switcher(call: cbq):
    """
    Обработка нажатия кнопки отображения/скрытия комплексных слов
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    slice_start = info.pop(mark_slice_start, 0)
    action = info.pop(mark_action, "")

    async with async_session_maker() as session:
        word = await (
            WordSelector()
            .filter_by(id=info[mark_record_id])
            .with_relationships()
            .scalar_async(session)
        )

        keyboard = WordKeyboard(word).keyboard_cpx(
            action=action, slice_start=slice_start
        )

    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
    )
