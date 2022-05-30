from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import ORDER_DELETE, ORDER_ADD, ORDER_DONE
from keyboards import keyboard_change, keyboard_delete


# Реакция на неправильно присланную информацию о удалениях
def error_answer(update: Update, context: CallbackContext) -> None:
    text = (
        f'Я не смог понять, сколько у тебя было удалений 😿. Пожалуйста, выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))

    return ORDER_DELETE


# Скинули заказ вместо количества удалений
def error_order(update: Update, context: CallbackContext) -> None:
    text = (
        f'Ты присылаешь новый номер заказа 😿. Пожалуйста, пришли сначала количество удалений по прошлому заказу, чтобы я мог посчитать твою статистику.'
    )
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))

    return ORDER_DELETE


# Скинули заказ вместо чека
def error_done(update: Update, context: CallbackContext) -> None:
    text = (
        f'Ты присылаешь новый номер заказа 😿. Пожалуйста, пришли сначала фото чека. Не забывай это делать вовремя, иначе я неправильно считаю статистику :('
    )
    reply_markup = InlineKeyboardMarkup(keyboard_change)
    update.message.reply_text(text, reply_markup=reply_markup)

    return ORDER_DONE


# Ошибка добавления позиции
def error_add(update: Update, context: CallbackContext) -> None:
    text = (
        f'Я не понял сколько позиций у тебя добавилось 😿'
        f'Пришли сообщением сколько их у тебя'
    )
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_change))

    return ORDER_ADD