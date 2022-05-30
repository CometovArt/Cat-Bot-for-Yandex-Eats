# Автозапуск бота лежит в /lib/systemd/system/catbot.service
# Рестарт бота systemctl restart catbot.service

import logging
import html
import json
import traceback
import random
import re
import pathlib

import cat  # Импорт файла с репликами кота
from config import bot, worksheet, TOKEN, ADMIN_CHAT, SBOR_CHAT, CHECK_CHAT, DEV_CHAT, LOGFILE  # Импорт токена

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler, PicklePersistence

from keyboards import keyboard_change, keyboard_delete
from errors import error_answer, error_order, error_done, error_add


# Логинг логов
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = "/cometovart/catbot/log_test.log")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = LOGFILE)
logger = logging.getLogger(__name__)

#callback_data
DELETE, ADD, DONE = range(3)


bot.send_message(DEV_CHAT, "Бот запущен")


# Начало диалога с ботом
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Для того, чтобы я мог считать твою статистику, просто перешли мне сообщение с заказом из @FoodfoxCourierBot',
    )


# Бот получил сообщение с заказом
def order_user(update: Update, context: CallbackContext) -> None:
    # Собираем данные о заказе
    msg = update.message.text
    user = update.message.from_user.username
    time = update.message.date.strftime("%H:%M")
    strings = re.findall(r'\n', msg)
    order = re.search(r'\d{6}-\d{6}', msg)
    time_end = re.search(r'\d\d:\d\d', msg)
    # Собираем сообщение о заказе
    text = (
        f'*Успехов в сборррке заказа {order.group(0)}!* 😽\n\n'
        f'Когда соберёшь заказ написать сколько у тебя было удалений\n\n'
        f'Нажми *«+ позиция»* если у тебя добавились позиции\n'
        f'Нажми *«Отмена»* если заказ отменился\n'
        f'Напиши *«+1»* чтобы добавить время к заказу\n\n'
        f'Если удалений небыло, то можешь сразу прислать фото чека!'
    )
    # Отправляем данные в чат и таблицу
    update.message.reply_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard_delete))
    val = worksheet.cell(3, 15).value # номер свободной ячейки
    worksheet.update_cell(val, 2, order.group(0)) # номер закака
    worksheet.update_cell(val, 3, user) # ник сборщика
    worksheet.update_cell(val, 4, time) # время начала сборки
    worksheet.update_cell(val, 6, len(strings)-13) # количество позиций
    worksheet.update_cell(val, 13, time_end.group(0)) # время доставки
    admin_reload(update, context)

    return DELETE


# Ответ на сообщение об удалении
def delete_answer(update: Update, context: CallbackContext) -> None:
    try:
        check_callback = update.callback_query.data
    except:
        delete = update.effective_message.text
        msg = update.message
        user = msg.from_user.username
    else:
        update.callback_query.answer()
        delete = check_callback
        msg = update.effective_message
        user = update.effective_user.username
    text = (
        f'*Я записал твои удаления!* 🖍\n\nТеперь жду фото чека ;)\n'
        f'_Пожалуйста, пришли его сразу после того, как отсканируешь_'
    )
    msg.reply_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard_change))
    # Записываем удаления в таблицу
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 7, delete)

    return DONE


# Ответ кнопку удаления
def none_answer_query(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()
    delete = update.callback_query.data # количество удалений
    text = (
        f'*Замурррррчательно! Ты молодчина!* \n\nТеперь жду фото чека ;)\n'
        f'_Пожалуйста, пришли его сразу после того, как отсканируешь_\n\n'
        f'Держи котейку за старания 😸'
    )
    update.effective_message.reply_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard_change))
    random_sticker = lambda: random.choice(cat.sticker_cat)
    update.effective_message.reply_sticker(sticker=random_sticker())
    # Записываем удаления в таблицу
    user = update.effective_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 7, delete)

    return DONE


# Ответ на кнопку добавления
def add_pos(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()
    text = (
        f'У тебя добавились позиции, отлично!\n\n'
        f'Пришли сообщением сколько их у тебя'
    )
    update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_change))

    return ADD


# Ответ на успешню запись
def add_answer(update: Update, context: CallbackContext) -> None:
    add = update.effective_message.text # количество добавлений
    text = (
        f'Я записал новые позиции ;) Теперь жду фото чека\n'
        f'Пожалуйста, пришли его сразу после того, как отсканируешь'
    )
    update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_change))
    # Записываем удаления в таблицу
    numb = f'-{add}'
    user = update.message.from_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 7, numb)

    return DONE


# Возвращаемся к удалениям
def delete_back(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()
    text = (
        f'Теперь ты можешь еще раз отметить количество удалений:'
    )
    update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))

    return DELETE


# Добавляем минуты
def add_min(update: Update, context: CallbackContext) -> None:
    min = re.search('\d{1,2}', update.effective_message.text) # сколько минут добавилось
    text = (
        f'Я добавил к твоему времени {min.group(0)} минут. А теперь выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))
    # Записываем удаления в таблицу
    user = update.effective_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 14, min.group(0))

    return DELETE


# Закрываем заказ
def done(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username
    time = update.effective_message.date.strftime("%H:%M")
    scan = worksheet.findall(user)[-1]
    worksheet.update_cell(scan.row, 8, time)
    val = worksheet.get('A{}:S{}'.format(scan.row, scan.row))
    text = (
        f'*Заказ {val[0][1]} успешно закрыт!* Твоя статистика за заказ:\n'
        f'🛒 Корзина: *{val[0][10]}*, ⏳ Время на позицию: *{val[0][11]}*\n\n'
        f'Твоя статистика за день:\n'
        f'🛒 Корзина: *{val[0][16]}*, ⏳ Время на позицию: *{val[0][17]}*, 💵 Ставка: *{val[0][18]}*р\n\n'
        f'Пересылай следующий заказ, как только придёт :)'
    )
    text_order = (
        f'Чек по заказу {val[0][1]}:'
    )
    update.effective_message.reply_text(text, parse_mode='markdown')
    bot.send_message(CHECK_CHAT, text_order)
    update.message.forward(CHECK_CHAT)
    admin_reload(update, context)

    return ConversationHandler.END


# Закрываем заказ после фото чека
def done_photo(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.username
    time = update.effective_message.date.strftime("%H:%M")
    scan = worksheet.findall(user)[-1]
    worksheet.update_cell(scan.row, 7, "0")
    worksheet.update_cell(scan.row, 8, time)
    val = worksheet.get('A{}:S{}'.format(scan.row, scan.row))
    text = (
        f'*Заказ {val[0][1]} успешно закрыт!* Твоя статистика за заказ:\n'
        f'🛒 Корзина: *{val[0][10]}*, ⏳ Время на позицию: *{val[0][11]}*\n\n'
        f'Твоя статистика за день:\n'
        f'🛒 Корзина: *{val[0][16]}*, ⏳ Время на позицию: *{val[0][17]}*, 💵 Ставка: *{val[0][18]}*р\n\n'
        f'Держи заслуженного котейку за заказ без удалений 😻'
    )
    text_order = (
        f'Чек по заказу {val[0][1]}:'
    )
    update.effective_message.reply_text(text, parse_mode='markdown')
    random_sticker = lambda: random.choice(cat.sticker_cat)
    update.effective_message.reply_sticker(sticker=random_sticker())
    bot.send_message(CHECK_CHAT, text_order)
    update.message.forward(CHECK_CHAT)
    admin_reload(update, context)

    return ConversationHandler.END


# Отменяем заказ
def stop(update: Update, context: CallbackContext) -> None:
    text = (
        f'Заказ отменён. Жду следующего ;)'
    )
    update.message.reply_text(text)
    # Записываем удаления в таблицу
    user = update.message.from_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 10, "Отмена")
    admin_reload(update, context)

    return ConversationHandler.END


# Отменяем заказ по кнопке
def stop_query(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()
    text = (
        f'Заказ отменён. Жду следующего ;)'
    )
    update.effective_message.reply_text(text)
    # Записываем удаления в таблицу
    user = update.effective_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 10, "Отмена")
    admin_reload(update, context)

    return ConversationHandler.END


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


# Список заказов в админку
def admin_reload(update: Update, context: CallbackContext) -> None:
    val = worksheet.get("V1:AA20")
    if val[0][4] == "0":
        orders = f'Нет заказов 😱'
    elif val[0][4] == "1":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]'
    elif val[0][4] == "2":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]'
    elif val[0][4] == "3":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]'
    elif val[0][4] == "4":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]'
    elif val[0][4] == "5":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]\n{val[5][3]} — {val[5][4]} [{val[5][5]}]'
    elif val[0][4] == "6":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]\n{val[5][3]} — {val[5][4]} [{val[5][5]}]\n{val[6][3]} — {val[6][4]} [{val[6][5]}]'
    elif val[0][4] == "7":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]\n{val[5][3]} — {val[5][4]} [{val[5][5]}]\n{val[6][3]} — {val[6][4]} [{val[6][5]}]\n{val[7][3]} — {val[7][4]} [{val[7][5]}]'
    elif val[0][4] == "8":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]\n{val[5][3]} — {val[5][4]} [{val[5][5]}]\n{val[6][3]} — {val[6][4]} [{val[6][5]}]\n{val[7][3]} — {val[7][4]} [{val[7][5]}]\n{val[8][3]} — {val[8][4]} [{val[8][5]}]'
    elif val[0][4] == "9":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]\n{val[5][3]} — {val[5][4]} [{val[5][5]}]\n{val[6][3]} — {val[6][4]} [{val[6][5]}]\n{val[7][3]} — {val[7][4]} [{val[7][5]}]\n{val[8][3]} — {val[8][4]} [{val[8][5]}]\n{val[9][3]} — {val[9][4]} [{val[9][5]}]'
    elif val[0][4] == "10":
        orders = f'{val[1][3]} — {val[1][4]} [{val[1][5]}]\n{val[2][3]} — {val[2][4]} [{val[2][5]}]\n{val[3][3]} — {val[3][4]} [{val[3][5]}]\n{val[4][3]} — {val[4][4]} [{val[4][5]}]\n{val[5][3]} — {val[5][4]} [{val[5][5]}]\n{val[6][3]} — {val[6][4]} [{val[6][5]}]\n{val[7][3]} — {val[7][4]} [{val[7][5]}]\n{val[8][3]} — {val[8][4]} [{val[8][5]}]\n{val[9][3]} — {val[9][4]} [{val[9][5]}]\n{val[10][3]} — {val[10][4]} [{val[10][5]}]'
    text = (
        f'Собираются:\n'
        f'{orders}\n\n'
        f'Собранные заказы:'
    )
    if val[0][1] == "1":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                ],
        ]
    elif val[0][1] == "2":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
        ]
    elif val[0][1] == "3":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                ],
        ]
    elif val[0][1] == "4":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
        ]
    elif val[0][1] == "5":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                ],
        ]
    elif val[0][1] == "6":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
        ]
    elif val[0][1] == "7":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                ],
        ]
    elif val[0][1] == "8":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
        ]
    elif val[0][1] == "9":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                ],
        ]
    elif val[0][1] == "10":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
        ]
    elif val[0][1] == "11":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                ],
        ]
    elif val[0][1] == "12":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
        ]
    elif val[0][1] == "13":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[13][0]} — {val[13][2]}', callback_data=str(f'{val[13][0]}')),
                ],
        ]
    elif val[0][1] == "14":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[13][0]} — {val[13][2]}', callback_data=str(f'{val[13][0]}')),
                    InlineKeyboardButton(f'{val[14][0]} — {val[14][2]}', callback_data=str(f'{val[14][0]}')),
                ],
        ]
    elif val[0][1] == "15":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[13][0]} — {val[13][2]}', callback_data=str(f'{val[13][0]}')),
                    InlineKeyboardButton(f'{val[14][0]} — {val[14][2]}', callback_data=str(f'{val[14][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[15][0]} — {val[15][2]}', callback_data=str(f'{val[15][0]}')),
                ],
        ]
    elif val[0][1] == "16":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[13][0]} — {val[13][2]}', callback_data=str(f'{val[13][0]}')),
                    InlineKeyboardButton(f'{val[14][0]} — {val[14][2]}', callback_data=str(f'{val[14][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[15][0]} — {val[15][2]}', callback_data=str(f'{val[15][0]}')),
                    InlineKeyboardButton(f'{val[16][0]} — {val[16][2]}', callback_data=str(f'{val[16][0]}')),
                ],
        ]
    elif val[0][1] == "17":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[13][0]} — {val[13][2]}', callback_data=str(f'{val[13][0]}')),
                    InlineKeyboardButton(f'{val[14][0]} — {val[14][2]}', callback_data=str(f'{val[14][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[15][0]} — {val[15][2]}', callback_data=str(f'{val[15][0]}')),
                    InlineKeyboardButton(f'{val[16][0]} — {val[16][2]}', callback_data=str(f'{val[16][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[17][0]} — {val[17][2]}', callback_data=str(f'{val[17][0]}')),
                ],
        ]
    elif val[0][1] == "18":
        keyboard = [
                [
                    InlineKeyboardButton(f'{val[1][0]} — {val[1][2]}', callback_data=str(f'{val[1][0]}')),
                    InlineKeyboardButton(f'{val[2][0]} — {val[2][2]}', callback_data=str(f'{val[2][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[3][0]} — {val[3][2]}', callback_data=str(f'{val[3][0]}')),
                    InlineKeyboardButton(f'{val[4][0]} — {val[4][2]}', callback_data=str(f'{val[4][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[5][0]} — {val[5][2]}', callback_data=str(f'{val[5][0]}')),
                    InlineKeyboardButton(f'{val[6][0]} — {val[6][2]}', callback_data=str(f'{val[6][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[7][0]} — {val[7][2]}', callback_data=str(f'{val[7][0]}')),
                    InlineKeyboardButton(f'{val[8][0]} — {val[8][2]}', callback_data=str(f'{val[8][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[9][0]} — {val[9][2]}', callback_data=str(f'{val[9][0]}')),
                    InlineKeyboardButton(f'{val[10][0]} — {val[10][2]}', callback_data=str(f'{val[10][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[11][0]} — {val[11][2]}', callback_data=str(f'{val[11][0]}')),
                    InlineKeyboardButton(f'{val[12][0]} — {val[12][2]}', callback_data=str(f'{val[12][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[13][0]} — {val[13][2]}', callback_data=str(f'{val[13][0]}')),
                    InlineKeyboardButton(f'{val[14][0]} — {val[14][2]}', callback_data=str(f'{val[14][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[15][0]} — {val[15][2]}', callback_data=str(f'{val[15][0]}')),
                    InlineKeyboardButton(f'{val[16][0]} — {val[16][2]}', callback_data=str(f'{val[16][0]}')),
                ],
                [
                    InlineKeyboardButton(f'{val[17][0]} — {val[17][2]}', callback_data=str(f'{val[17][0]}')),
                    InlineKeyboardButton(f'{val[18][0]} — {val[18][2]}', callback_data=str(f'{val[18][0]}')),
                ],
        ]
    if val[0][1] == "0":
        bot.send_message(ADMIN_CHAT, text)
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(ADMIN_CHAT, text, reply_markup=reply_markup)


# Отмечаем выданный заказ
def admin_done(update: Update, context: CallbackContext) -> None:
    dt = update.callback_query
    bot.send_message(ADMIN_CHAT, text=f'dtd{dt}')
    update.callback_query.answer()
    torder = re.compile(r'\d{6}[-]%s' % (update.callback_query.data))
    scan = worksheet.findall(torder)[-1] # ищем заказ
    worksheet.update_cell(scan.row, 10, "Выдан")
    admin_reload(update, context)


# Кот говорит мяу
def talk(update: Update, context: CallbackContext) -> None:
    random_message = lambda: random.choice(cat.talk)
    random_voice = lambda: random.choice(cat.tvoice_cat)
    random_sticker = lambda: random.choice(cat.sticker_cat)
    stat = lambda: random.choice(['1','2','3'])
    if stat() == "1":
        update.message.reply_text(random_message())
    elif stat() == "2":
        update.message.reply_voice(open(pathlib.Path('voice', random_voice()), 'rb'))
    else:
        update.message.reply_sticker(sticker=random_sticker())


# Кот шипит
def test_voice(update: Update, context: CallbackContext) -> None:
    random_voice = lambda: random.choice(cat.tvoice_cat)
    duration = int = None
    update.message.reply_voice(open(pathlib.Path('voice', random_voice()), 'rb'))


# Обновляем админку
def callback_reload(update: Update, context: CallbackContext) -> None:
    admin_reload(update, context)


# Обновляем админку
def id(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.effective_message.chat.id)


# Обновляем админку
def test(update: Update, context: CallbackContext) -> None:
    try:
        update.callback_query.data
    except:
        text = "исключние"
        update.message.reply_text(f'текст{text}')
    else:
        text = "или"
        update.effective_message.reply_text(f'текст{text}')


# Кот шипит
def woof(update: Update, context: CallbackContext) -> None:
    random_voice = lambda: random.choice(cat.shh_cat)
    update.message.reply_voice(open(random_voice(), 'rb'))


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

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

    # Finally, send the message
    context.bot.send_message(chat_id=ADMIN_CHAT, text=message, parse_mode=ParseMode.HTML)


def main() -> None:
    persistence = PicklePersistence(filename='conversationbot')
    updater = Updater(TOKEN, persistence=persistence)
    dispatcher = updater.dispatcher

    # Слушает сообщения от всех и мявкает в ответ
    dispatcher.add_handler(MessageHandler(Filters.regex(cat.listen_talk) & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('(Яндекс|яндекс|Фудфокс|фудфокс)'), talk))
    dispatcher.add_handler(MessageHandler(Filters.regex(cat.listen_woof) & ~Filters.regex('\d{6}-\d{6}'), woof))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('stat', stat))
    dispatcher.add_handler(CommandHandler('reload', callback_reload))
    dispatcher.add_handler(CommandHandler('id', id))
    dispatcher.add_handler(CommandHandler('test_voice', test_voice))

    dispatcher.add_handler(MessageHandler(Filters.regex('тест'), test))

    # Слушает чат сборки и собирает номера заказов
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('\d{6}-\d{6}') & ~Filters.chat(SBOR_CHAT), order_user)],
        states={
            DELETE: [
                MessageHandler(Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('^[+]\d{,2}$'), delete_answer),
                MessageHandler(Filters.text & ~Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('^[+]\d{,2}$'), error_answer),
                MessageHandler(Filters.regex('\d{6}-\d{6}'), error_order),
                MessageHandler(Filters.regex('^[+]\d{,2}$') & ~Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}'), add_min),
                CallbackQueryHandler(delete_answer, pattern='^' + str('\d{1}') + '$'),
                CallbackQueryHandler(add_pos, pattern='^' + str('add_pos') + '$'),
                CallbackQueryHandler(test, pattern='^' + str('cancel_order') + '$'),
                MessageHandler(Filters.photo, done_photo),
            ],
            ADD: [
                MessageHandler(Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('^[+]\d{,2}$'), add_answer),
                MessageHandler(~Filters.regex('^\d{,2}$'), error_add),
                CallbackQueryHandler(delete_back, pattern='^' + str('delete_back') + '$'),
            ],
            DONE: [
                MessageHandler(Filters.photo, done),
                MessageHandler(Filters.regex('\d{6}-\d{6}'), error_done),
                CallbackQueryHandler(delete_back, pattern='^' + str('delete_back') + '$'),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('(Отмена|отмена|Отменяется|отменяется|Отменен|отменен|Отменён|отменён|Отменится|отменится)'), stop)],
    )


    dispatcher.add_handler(CallbackQueryHandler(admin_done, pattern='^' + str('\d{6}') + '$'))
    dispatcher.add_error_handler(error_handler)

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
