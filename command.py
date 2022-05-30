from telegram import Update
from telegram.ext import CallbackContext

import random
import pathlib
import datetime

# Импорт файла с репликами кота
import cat
from admin import admin_reload
from config import worksheet


# Начало диалога с ботом
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Для того, чтобы я мог считать твою статистику, просто перешли мне сообщение с заказом из @FoodfoxCourierBot',
    )
    

# Выдаём статистику
def stat(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.username
    scan = worksheet.findall(user)[-1]
    val = worksheet.get('Q{}:S{}'.format(scan.row, scan.row))
    text = (
        f'Твоя статистика за день:\n'
        f'Корзина: {val[0][0]}, Время на позицию: {val[0][1]}, Ставка: {val[0][2]}р\n\n'
    )
    update.effective_message.reply_text(text)


# Обновляем админку
def callback_reload(update: Update, context: CallbackContext) -> None:
    admin_reload(update, context)


# Обновляем админку
def id(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.effective_message.chat.id)


# Обновляем админку
def test(update: Update, context: CallbackContext) -> None:
    date = datetime.datetime.today().strftime("%H-%M")
    date2 = datetime.datetime.today().strftime("%d-%m")
    text = (
        f'{date} * {date2}'
    )
    update.message.reply_text(text)


# Кот шипит
def test_voice(update: Update, context: CallbackContext) -> None:
    random_voice = lambda: random.choice(cat.voice)
    update.message.reply_voice(open(pathlib.Path('voice', random_voice()), 'rb'))