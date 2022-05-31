from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

import re

from config import bot, worksheet, ADMIN_CHAT


# Список заказов в админку
async def admin_reload(update: Update, context: CallbackContext) -> None:
    val = worksheet.get("AE1:AN20")

    order_list = [] # собираются

    if int(val[0][1]) != 0:
        for i in range(1, int(val[0][1]) + 1):
            order_list.append(f'{val[i][0]} — {val[i][1]} [{val[i][2]}]\n')
    else:
        order_list.append(f'Нет заказов 😱 \n')

    order_callback = [] # собраны

    if int(val[0][5]) != 0:
        for i in range(1, int(val[0][5]) + 1):
            order_callback.append(f'{val[i][4]}')

    order_button = [] 

    if int(val[0][5]) != 0:
        for i in range(1, int(val[0][5]) + 1):
            order_button.append(f'{val[i][4]} — {val[i][5]}')
        for n in range(1, (18 - int(val[0][5])) + 1):
            order_button.append('')
            order_callback.append('404')
    else:
        for n in range(1, 18 + 1):
            order_button.append('')
            order_callback.append('404')

    # order_time = [] # просрочены

    # if int(val[0][8]) != 0:
    #     order_time.append(f'Просроченные заказы:\n')
    #     for i in range(1, int(val[0][8]) + 1):
    #         order_time.append(f'{val[i][7]} — {val[i][8]} [{val[i][9]}]\n')
    #     order_time.append(f'\n')
    # else:
    #     order_time.append('')

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

    if val[0][5] == "0":
        text_plus = "\nВсе заказы выданы 💪"
    else:
        text_plus = ""

    text = (
        f'Собираются:\n'
        f'{"".join(order_list)}\n'
        # f'{"".join(order_time)}'
        f'Собранные:{text_plus}'
    )

    if val[0][5] == "0":
        await bot.send_message(ADMIN_CHAT, text)

    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(ADMIN_CHAT, text, reply_markup=reply_markup)


# Отмечаем выданный заказ
async def admin_done(update: Update, context: CallbackContext) -> None:
    await update.callback_query.answer()

    torder = re.compile(r'\d{6}[-]%s' % (update.callback_query.data))
    scan = worksheet.findall(torder)[-1]  # ищем заказ
    worksheet.update_cell(scan.row, 10, "Выдан")

    await admin_reload(update, context)