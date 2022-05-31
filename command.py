from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import random
import pathlib

# Импорт файла с репликами кота
import cat
from admin import admin_reload
from config import DEV_CHAT, bot, statsheet, number_week


# Начало диалога с ботом
async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f'Привет {user.mention_markdown_v2()}\! Для того, чтобы я мог считать твою статистику, просто перешли мне сообщение с заказом из @FoodfoxCourierBot',
    )


# Выдаём статистику
async def stat(update: Update, context: CallbackContext) -> None:
    update = update.message
    user = update.from_user.username
    try:
        scan_week = statsheet.find(f'Week{number_week}')
        scan_user = statsheet.find(user)
    except:
        text = (
            f'Я не нашел твоей статистики :('
            )
    else:
        val = statsheet.get('R{}C{}:R{}C{}'.format(scan_week.row-7, scan_user.col, scan_week.row, scan_user.col+3))
        
        stat_list = [] # собираются
        day_list = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        for i in range(0, 6):
            try:
                stat_list.append(f'*{day_list[i]} —* 🛒 {val[i][0]} | ⏳ {val[i][1]} | 💵 {val[i][2]} | 📦 {val[i][3]}\n')
            except:
                i
            
        text = (
            f'Твоя статистика за неделю:\n\n'
            f'🛒 Корзина: *{val[7][0]}*, ⏳ На позицию: *{val[7][1]}*,\n'
            f'💵 Ставка: *{val[7][2]}*, 📦 Заказов: *{val[7][3]}*\n\n\n'
            f'Твоя статистика по дням:\n\n'
            f'{"".join(stat_list)}\n\n'
            f'_В ежедневной статистике указывается прогнозируемая ставка, она не учитывает количество заказов._\n\n' 
            f'_В еженедельной статистике количество заказов влияет на ставку_.'
            )
    
    await update.reply_text(text, parse_mode='markdown')


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