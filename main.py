# Автозапуск бота лежит в /lib/systemd/system/catbot.service
# Рестарт бота systemctl restart catbot.service

import logging
import random
import re
import time

import cat  # Импорт файла с репликами кота
from config import bot, worksheet, TOKEN, ADMIN_CHAT, SBOR_CHAT  # Импорт токена

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler


# Логинг логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = "/cometovart/catbot/log.log")
logger = logging.getLogger(__name__)


DELETE, DONE = range(2)


def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Для того, чтобы я мог считать твою статистику, просто перешли мне сообщение с заказом из @FoodfoxCourierBot',
    )


# Импорт сообщения о заказе
def order_chat(update: Update, context: CallbackContext) -> None:
    # Собираем данные о заказе
    time = update.message.date.strftime("%H:%M")
    order = re.search(r'\d{6}-\d{6}', update.message.text)
    user = update.message.from_user.username
    strings = re.findall(r'\n', update.message.text)
    # Собираем сообщение о заказе
    keyboard = [
            [
                InlineKeyboardButton("Выдан", callback_data=str(close)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f'Заказ {order.group(0)}\n'
        f'Собирает @{user}\n {len(strings)-13}'
    )
    # Отправляем данные в чат
    bot.send_message(SBOR_CHAT, text, reply_markup=reply_markup)


def order_user(update: Update, context: CallbackContext) -> None:
    # Собираем данные о заказе
    time = update.message.date.strftime("%H:%M")
    order = re.search(r'\d{6}-\d{6}', update.message.text)
    user = update.message.from_user.username
    strings = re.findall(r'\n', update.message.text)
    time_end = re.search(r'\d\d:\d\d', update.message.text)
    # Собираем сообщения о заказе
    text = (
        f'Успехов в сборке заказа {order.group(0)}!\n'
        f'Когда заказ будет собран напиши сколько было удалений'
    )
    keyboard = [
            [
                InlineKeyboardButton("Выдан", callback_data=str(close)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text2 = (
        f'Заказ {order.group(0)}\n'
        f'Собирает {user}\n'
    )
    # Отправляем данные в чат и таблицу
    update.message.reply_text(text)
    bot.send_message(SBOR_CHAT, text2) #чат сборщиков
    bot.send_message(ADMIN_CHAT, text2, reply_markup=reply_markup) #админка
    val = worksheet.cell(3, 15).value
    worksheet.update_cell(val, 2, order.group(0))
    worksheet.update_cell(val, 3, user)
    worksheet.update_cell(val, 4, time)
    worksheet.update_cell(val, 6, len(strings)-13)
    worksheet.update_cell(val, 13, time_end.group(0))

    return DELETE


def delete_answer(update: Update, context: CallbackContext) -> None:
    delete = update.effective_message.text
    user = update.message.from_user.username
    text = (
        f'Удаления записаны! Нажми кнопку ниже, когда отсканируешь чек'
    )
    keyboard = [
            [
                InlineKeyboardButton("Отсканировал чек", callback_data=str(done)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 7, delete)

    return DONE


def done(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user = update.effective_user.username
    time = update.effective_message.date.strftime("%H:%M")
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 8, time)
    stat_check = worksheet.cell(val.row, 11).value
    stat_time = worksheet.cell(val.row, 12).value
    text = (
        f'Заказ успешно закрыт. Твоя статистика:\n'
        f'Корзина: {stat_check}, Время на позицию: {stat_time}\n'

        f'Пересылай следующий заказ, как только придёт :)'
    )
    update.effective_message.reply_text(text)

    return ConversationHandler.END


def stop(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.username
    text = (
        f'Заказ отменён. Жду следующего ;)'
    )
    update.message.reply_text(text)
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 10, "Отмена")

    return ConversationHandler.END


# Подтверждение выдачи заказа
def close(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    order = re.search(r'\d{6}-\d{6}', update.effective_message.text)
    text = (
        f'Заказ выдан'
    )
    query.edit_message_text(text)
    val = worksheet.find(order.group(0))
    worksheet.update_cell(val.row, 10, "Выдан")
    time.sleep(1)
    query.delete_message()
    lst = worksheet.cell(4, 12).value
    bot.edit_message_text(lst, chat_id=ADMIN_CHAT, message_id=7)


# Кот говорит мяу
def talk(update: Update, context: CallbackContext) -> None:
    random_message = lambda: random.choice(cat.talk)
    update.message.reply_text(random_message())



def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Слушает сообщения от всех и мявкает в ответ
    dispatcher.add_handler(MessageHandler(Filters.regex(cat.listen) & ~Filters.regex('\d{6}-\d{6}'), talk))

    # Слушает чат сборки и собирает номера заказов
    dispatcher.add_handler(MessageHandler(Filters.regex('\d{6}-\d{6}') & Filters.chat(SBOR_CHAT), order_chat))

    # Слушает тапы по кнопке удаления
    dispatcher.add_handler(CallbackQueryHandler(close, pattern='^' + str(close) + '$'))

    dispatcher.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('\d{6}-\d{6}') & ~Filters.chat(SBOR_CHAT), order_user)],
        states={
            DELETE: [MessageHandler(Filters.text & ~Filters.regex('(Отмена|отмена)'), delete_answer)],
            DONE: [CallbackQueryHandler(done, pattern='^' + str(done) + '$')],
        },
        fallbacks=[MessageHandler(Filters.regex('(Отмена|отмена)'), stop)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
