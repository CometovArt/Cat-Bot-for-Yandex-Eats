from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

import logging
import html
import json
import traceback

from config import DEV_CHAT, ORDER_DELETE, ORDER_ADD, ORDER_DONE
from keyboards import keyboard_change, keyboard_delete


# Реакция на неправильно присланную информацию о удалениях
async def error_answer(update: Update, context: CallbackContext) -> None:
    text = (
        f'Я не смог понять, сколько у тебя было удалений 😿. Пожалуйста, выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))

    return ORDER_DELETE


# Скинули заказ вместо количества удалений
async def error_order(update: Update, context: CallbackContext) -> None:
    text = (
        f'Ты присылаешь новый номер заказа 😿. Пожалуйста, пришли сначала количество удалений по прошлому заказу, чтобы я мог посчитать твою статистику.'
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))

    return ORDER_DELETE


# Скинули заказ вместо чека
async def error_done(update: Update, context: CallbackContext) -> None:
    text = (
        f'Ты присылаешь новый номер заказа 😿. Пожалуйста, пришли сначала фото чека. Не забывай это делать вовремя, иначе я неправильно считаю статистику :('
    )
    reply_markup = InlineKeyboardMarkup(keyboard_change)
    await update.message.reply_text(text, reply_markup=reply_markup)

    return ORDER_DONE


# Ошибка добавления позиции
async def error_add(update: Update, context: CallbackContext) -> None:
    text = (
        f'Я не понял сколько позиций у тебя добавилось 😿'
        f'Пришли сообщением сколько их у тебя'
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_change))

    return ORDER_ADD


async def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logging.getLogger(__name__).error(msg="Exception while handling an update:", exc_info=context.error)
    
    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
        )
    try:
        # Finally, send the message
        await context.bot.send_message(chat_id=DEV_CHAT, text=message, parse_mode=ParseMode.HTML)
    except:
        await context.bot.send_message(chat_id=DEV_CHAT, text='Ошибка в ошибке :(')