from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from config import sh, SETTING_NAME, SETTING_NAME_DONE
from keyboards import keyboard_name


async def setting_user(update: Update, context: CallbackContext) -> None:
    text = (
        f'Здесь ты можешь настроить бота под себя.'
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_name))

    return SETTING_NAME


async def setting_edit_name(update: Update, context: CallbackContext) -> None:
    await update.callback_query.answer()
    text = (
        f'Как тебя зовут?'
    )
    await update.effective_message.reply_text(text)

    return SETTING_NAME_DONE


async def setting_edit_name_error(update: Update, context: CallbackContext) -> None:
    text = (
        f'Не понял :('
    )
    await update.effective_message.reply_text(text)

    return SETTING_NAME_DONE


async def setting_edit_name_done(update: Update, context: CallbackContext) -> None:
    name = update.effective_message.text
    user = update.effective_user.username
    text = (
        f'Приятно познакомиться, {name}'
    )
    await update.message.reply_text(text)
    statsheet = sh.worksheet('Stat')
    scan = statsheet.find(user) # ищем последний заказ
    statsheet.update_cell(2, scan.col, name)

    return ConversationHandler.END