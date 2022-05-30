from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import random
import pathlib
from config import DEV_CHAT, bot, worksheet
from datetime import datetime

# Импорт файла с репликами кота
import cat
from admin import admin_reload
from config import worksheet, timetest


# Начало диалога с ботом
async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f'Привет {user.mention_markdown_v2()}\! Для того, чтобы я мог считать твою статистику, просто перешли мне сообщение с заказом из @FoodfoxCourierBot',
    )
    

# Выдаём статистику
async def stat(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.username
    try:
        scan = worksheet.findall(user)[-1]
    except:
        text = (
            f'Я не нашел твоей статистики :('
            )
    else:
        val = worksheet.get('T{}:AC{}'.format(scan.row, scan.row))
        text = (
            f'Твоя статистика за день:\n'
            f'Корзина: {val[0][0]}, Время на позицию: {val[0][1]},\n'
            f'Ставка: {val[0][2]}, Заказы: {val[0][3]}\n\n'
            f'Твоя статистика за неделю:\n'
            f'Корзина: {val[0][6]}, Время на позицию: {val[0][7]},\n'
            f'Ставка: {val[0][8]}, Заказы: {val[0][9]}\n'
            )
    await update.effective_message.reply_text(text)


# Обновляем админку
async def callback_reload(update: Update, context: CallbackContext) -> None:
    await admin_reload(update, context)


# Обновляем админку
async def getid(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(update.effective_message.chat.id)


# Обновляем админку
async def test(update: Update, context: CallbackContext) -> None:
    random_message = lambda: random.choice(cat.talk)
    random_message2 = lambda: random.choice(cat.talk)
    keyboard_0 = [
        [
            InlineKeyboardButton('123', callback_data=str('123')),
        ],
    ]
    await bot.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard_0), chat_id=DEV_CHAT, message_id=1102)


# Кот шипит
async def test_voice(update: Update, context: CallbackContext) -> None:
    random_voice = lambda: random.choice(cat.voice)
    await update.message.reply_voice(open(pathlib.Path('voice', random_voice()), 'rb'))