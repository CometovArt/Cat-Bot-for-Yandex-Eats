# Автозапуск бота лежит в /lib/systemd/system/catbot.service
# Рестарт бота systemctl restart catbot.service

import logging
import random
import re
import time

import cat  # Импорт файла с репликами кота
from config import bot, TOKEN, ADMIN_CHAT  # Импорт токена

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CallbackQueryHandler


# Логи
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = "/cometovart/catbot/log.log")
logger = logging.getLogger(__name__)


# Импорт сообщения о заказе
def order(update: Update, context: CallbackContext) -> None:
    order = re.search(r'\d{6}-\d{6}', update.message.text)
    user = update.message.from_user.username
    # Собираем сообщение о заказе
    keyboard = [
            [
                InlineKeyboardButton("Собран", callback_data=str(done)),
                 InlineKeyboardButton("Выдан", callback_data=str(close)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f'Заказ {order.group(0)}\n'
        f'Собирает @{user}\n'
    )
    # Отправляем данные в чат
    bot.send_message(ADMIN_CHAT, text, reply_markup=reply_markup)


# Подтверждение выдачи заказа
def done(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    order = re.search(r'\d{6}-\d{6}', update.effective_message.text)
    text = (f'Заказ {order.group(0)} собран')
    keyboard = [
        [InlineKeyboardButton("Выдан", callback_data=str(close))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(ADMIN_CHAT, text, reply_markup=reply_markup)
    query.delete_message()
    

# Подтверждение выдачи заказа
def close(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    text = ('Заказ выдан')
    query.edit_message_text(text)
    time.sleep(1)
    query.delete_message()


# Кот говорит мяу
def talk(update: Update, context: CallbackContext) -> None:
    random_message = lambda: random.choice(cat.talk)
    update.message.reply_text(random_message())


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Слушает сообщения от всех и мявкает в ответ
    dispatcher.add_handler(MessageHandler(Filters.regex(cat.listen), talk))

    # Слушает чат сборки и собирает номера заказов
    dispatcher.add_handler(MessageHandler(Filters.regex('\d{6}-\d{6}'), order))

    # Слушает тапы по кнопке удаления
    dispatcher.add_handler(CallbackQueryHandler(done, pattern='^' + str(done) + '$'))
    dispatcher.add_handler(CallbackQueryHandler(close, pattern='^' + str(close) + '$'))


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()