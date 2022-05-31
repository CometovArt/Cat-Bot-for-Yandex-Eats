from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

#import random
import re
from datetime import datetime

import cat
from config import bot, worksheet, CHECK_CHAT, ORDER_DELETE, ORDER_ADD, ORDER_DONE
from admin import admin_reload
from keyboards import keyboard_delete, keyboard_change


# Бот получил сообщение с заказом
async def order_user(update: Update, context: CallbackContext) -> None:
    # Собираем данные о заказе
    update = update.message
    message = update.text
    user = update.from_user.username
    day = datetime.now().strftime("%d.%m")
    timez = datetime.now().strftime("%H:%M")
    strings = re.findall(r'\n', message)
    order = re.search(r'\d{6}-\d{6}', message)
    time_end = re.search(r'\d\d:\d\d', message)
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
    await update.reply_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard_delete))
    val = worksheet.cell(1, 1).value                    # номер свободной ячейки
    worksheet.update_cell(val, 1, day)                  # день сборки
    worksheet.update_cell(val, 2, order.group(0))       # номер закака
    worksheet.update_cell(val, 3, user)                 # ник сборщика
    worksheet.update_cell(val, 4, timez)                # время начала сборки
    worksheet.update_cell(val, 5, len(strings)-13)      # количество позиций
    worksheet.update_cell(val, 9, time_end.group(0))    # время доставки
    await admin_reload(update, context)

    return ORDER_DELETE


# Ответ на сообщение об удалении
async def delete_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    try:
        check = query.data
    except:
        update = update.message
        delete = update.text
        user = update.from_user.username
    else:
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)
        delete = check
        update = query.message
        user = update.chat.username
    text = (
        f'*Я записал твои удаления!* 🖍\n\nТеперь жду фото чека ;)\n'
        f'_Пожалуйста, пришли его сразу после того, как отсканируешь_'
    )
    await update.reply_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard_change))
    # Записываем удаления в таблицу
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 6, delete)

    return ORDER_DONE


# Ответ на кнопку добавления
async def add_pos(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    text = (
        f'У тебя добавились позиции, отлично!\n\n'
        f'Пришли сообщением сколько их у тебя'
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_change))

    return ORDER_ADD


# Ответ на успешню запись
async def add_answer(update: Update, context: CallbackContext) -> None:
    update = update.message
    add = update.text # количество добавлений
    text = (
        f'Я записал новые позиции ;) Теперь жду фото чека\n'
        f'Пожалуйста, пришли его сразу после того, как отсканируешь'
    )
    await update.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_change))
    # Записываем удаления в таблицу
    numb = f'-{add}'
    user = update.from_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 6, numb)

    return ORDER_DONE


# Возвращаемся к удалениям
async def delete_back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    text = (
        f'Теперь ты можешь еще раз отметить количество удалений:'
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))

    return ORDER_DELETE


# Добавляем минуты
async def add_min(update: Update, context: CallbackContext) -> None:
    update = update.message
    minute = re.search('\d{1,2}', update.text) # сколько минут добавилось
    text = (
        f'Я добавил к твоему времени {min.group(0)} минут. А теперь выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    await update.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_delete))
    # Записываем удаления в таблицу
    user = update.from_user.username
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 7, minute.group(0))

    return ORDER_DELETE


# Закрываем заказ
async def done(update: Update, context: CallbackContext) -> None:
    update = update.message
    user = update.from_user.username
    time_now = datetime.now().strftime("%H:%M")
    scan = worksheet.findall(user)[-1]
    worksheet.update_cell(scan.row, 8, time_now)
    val = worksheet.get('A{}:AC{}'.format(scan.row, scan.row))
    text = (
        f'*Заказ {val[0][1]} успешно закрыт!* Твоя статистика за заказ:\n'
        f'🛒 Корзина: *{val[0][15]}*, ⏳ Время на позицию: *{val[0][16]}*\n\n'
        f'Твоя статистика за день:\n'
        f'🛒 Корзина: *{val[0][19]}*, ⏳ Время на позицию: *{val[0][20]}*, 💵 Ставка: *{val[0][21]}*, Заказов: *{val[0][22]}*\n\n'
        f'Пересылай следующий заказ, как только придёт :)'
    )
    text_order = (
        f'Чек по заказу {val[0][1]}:'
    )
    await update.reply_text(text, parse_mode='markdown')
    await bot.send_message(CHECK_CHAT, text_order)
    await update.forward(CHECK_CHAT)
    await admin_reload(update, context)

    return ConversationHandler.END


# Закрываем заказ после фото чека
async def done_photo(update: Update, context: CallbackContext) -> None:
    update = update.message
    user = update.from_user.username
    time = datetime.now().strftime("%H:%M")
    scan = worksheet.findall(user)[-1]
    worksheet.update_cell(scan.row, 6, "0")
    worksheet.update_cell(scan.row, 8, time)
    val = worksheet.get('A{}:AC{}'.format(scan.row, scan.row))
    text = (
        f'*Заказ {val[0][1]} успешно закрыт!* Твоя статистика за заказ:\n'
        f'🛒 Корзина: *{val[0][15]}*, ⏳ Время на позицию: *{val[0][16]}*\n\n'
        f'Твоя статистика за день:\n'
        f'🛒 Корзина: *{val[0][19]}*, ⏳ Время на позицию: *{val[0][20]}*,\n 💵 Ставка: *{val[0][21]}*, Заказов: *{val[0][22]}*\n\n'
        f'Пересылай следующий заказ, как только придёт :)'
    )
    text_order = (
        f'Чек по заказу {val[0][1]}:'
    )
    await update.reply_text(text, parse_mode='markdown')
    #random_sticker = lambda: random.choice(cat.sticker)
    #await update.reply_sticker(sticker=random_sticker())
    await bot.send_message(CHECK_CHAT, text_order)
    await update.forward(CHECK_CHAT)
    await admin_reload(update, context)

    return ConversationHandler.END


# Отменяем заказ
async def order_cancel(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    try:
        query.data
    except:
        update = update.message
        user = update.from_user.username
    else:
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)
        update = query.message
        user = update.chat.username
        
    text = (f'Заказ отменён. Жду следующего ;)')
    await update.reply_text(text)
    
    # Записываем удаления в таблицу
    scan = worksheet.findall(user)[-1] # ищем последний заказ
    worksheet.update_cell(scan.row, 10, "Отмена")
    await admin_reload(update, context)

    return ConversationHandler.END


async def order_close(update: Update, context: CallbackContext) -> None:
    text = (f'Заказ отменён. Жду следующего ;)')
    await update.message.reply_text(text)

    return ConversationHandler.END