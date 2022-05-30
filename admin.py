from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

import re

from config import bot, worksheet, ADMIN_CHAT


# Список заказов в админку
def admin_reload(update: Update, context: CallbackContext) -> None:
    val = worksheet.get("V1:AA20")

    order_list = []

    if int(val[0][4]) != 0:
        for i in range(1, int(val[0][4]) + 1):
            order_list.append(f'{val[i][3]} — {val[i][4]} [{val[i][5]}]\n')
    else:
        order_list.append(f'Нет заказов 😱 \n')

    order_callback = []

    if int(val[0][1]) != 0:
        for i in range(1, int(val[0][1]) + 1):
            order_callback.append(f'{val[i][0]}')

    order_button = []

    if int(val[0][1]) != 0:
        for i in range(1, int(val[0][1]) + 1):
            order_button.append(f'{val[i][0]} — {val[i][2]}')
        for n in range(1, (18 - int(val[0][1])) + 1):
            order_button.append('')
            order_callback.append('404')
    else:
        for n in range(1, 18 + 1):
            order_button.append('')
            order_callback.append('404')

    keyboard = [
                [
                    InlineKeyboardButton(f'{order_button[0]}', callback_data=str(f'{order_callback[0]}')),
                    InlineKeyboardButton(f'{order_button[1]}', callback_data=str(f'{order_callback[1]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[2]}', callback_data=str(f'{order_callback[2]}')),
                    InlineKeyboardButton(f'{order_button[3]}', callback_data=str(f'{order_callback[3]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[4]}', callback_data=str(f'{order_callback[4]}')),
                    InlineKeyboardButton(f'{order_button[5]}', callback_data=str(f'{order_callback[5]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[6]}', callback_data=str(f'{order_callback[6]}')),
                    InlineKeyboardButton(f'{order_button[7]}', callback_data=str(f'{order_callback[7]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[8]}', callback_data=str(f'{order_callback[8]}')),
                    InlineKeyboardButton(f'{order_button[9]}', callback_data=str(f'{order_callback[9]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[10]}', callback_data=str(f'{order_callback[10]}')),
                    InlineKeyboardButton(f'{order_button[11]}', callback_data=str(f'{order_callback[11]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[12]}', callback_data=str(f'{order_callback[12]}')),
                    InlineKeyboardButton(f'{order_button[13]}', callback_data=str(f'{order_callback[13]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[14]}', callback_data=str(f'{order_callback[14]}')),
                    InlineKeyboardButton(f'{order_button[15]}', callback_data=str(f'{order_callback[15]}')),
                ],
                [
                    InlineKeyboardButton(f'{order_button[16]}', callback_data=str(f'{order_callback[16]}')),
                    InlineKeyboardButton(f'{order_button[17]}', callback_data=str(f'{order_callback[17]}')),
                ],
    ]

    if val[0][1] == "0":
        text_plus = "\nВсе заказы выданы 💪"
    else:
        text_plus = ""

    text = (
        f'Собираются:\n'
        f'{"".join(order_list)}\n'
        f'Собранные:{text_plus}'
    )

    if val[0][1] == "0":
        bot.send_message(ADMIN_CHAT, text)

    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(ADMIN_CHAT, text, reply_markup=reply_markup)


# Отмечаем выданный заказ
def admin_done(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()

    torder = re.compile(r'\d{6}[-]%s' % (update.callback_query.data))
    scan = worksheet.findall(torder)[-1] # ищем заказ
    worksheet.update_cell(scan.row, 10, "Выдан")

    admin_reload(update, context)