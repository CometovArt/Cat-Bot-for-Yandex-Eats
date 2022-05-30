# Автозапуск бота лежит в /lib/systemd/system/catbot.service
# Рестарт бота systemctl restart catbot.service

import logging
import random
import re

import cat  # Импорт файла с репликами кота
from config import bot, worksheet, TOKEN, ADMIN_CHAT, SBOR_CHAT, CHECK_CHAT  # Импорт токена

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler

# Логинг логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = "/cometovart/catbot/log.log")
logger = logging.getLogger(__name__)


DELETE, DONE = range(2)
order10, order20, order30, order40, order50, order60, order70, order80, order90 = range(9)


def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Для того, чтобы я мог считать твою статистику, просто перешли мне сообщение с заказом из @FoodfoxCourierBot',
    )


# Импорт сообщения о заказе
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
        f'Когда заказ будет собран напиши или выбери на кнопке сколько было удалений\n\n'
        f'Если номер заказа был отправлен не сразу, то ты можешь написать мне насколько поздно был прислан номер. Это сделает подсчет твоей статистики еще точнее. \n\nДля этого напиши мне количество минут в таком формате: "+5", без ковычек'
    )
    keyboard = [
            [
                InlineKeyboardButton("Выдан", callback_data=str(close)),
            ],
    ]
    keyboard2 = [
            [
                InlineKeyboardButton("1", callback_data=str(1)),
                InlineKeyboardButton("2", callback_data=str(2)),
                InlineKeyboardButton("3", callback_data=str(3)),
            ],
            [
                InlineKeyboardButton("4", callback_data=str(4)),
                InlineKeyboardButton("5", callback_data=str(5)),
                InlineKeyboardButton("6", callback_data=str(6)),
            ],
            [
                InlineKeyboardButton("7", callback_data=str(7)),
                InlineKeyboardButton("8", callback_data=str(8)),
                InlineKeyboardButton("9", callback_data=str(9)),
            ],
            [
                InlineKeyboardButton("0", callback_data=str(0)),
                InlineKeyboardButton("Отмена", callback_data=str(stop_query)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    reply_markup2 = InlineKeyboardMarkup(keyboard2)
    text2 = (
        f'Заказ {order.group(0)}\n'
        f'Собирает {user}\n'
    )
    # Отправляем данные в чат и таблицу
    update.message.reply_text(text, reply_markup=reply_markup2)
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
                InlineKeyboardButton("Чек отсканирован", callback_data=str(done)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 7, delete)

    return DONE


def delete_answer_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    delete = update.callback_query.data
    user = update.effective_user.username
    text = (
        f'Я записал твои удаления! Теперь жду фото чека ;)\n'
        f'Пожалуйста, пришли его сразу после того, как отсканируешь'
    )
    update.effective_message.reply_text(text)
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 7, delete)

    return DONE


def add_min(update: Update, context: CallbackContext) -> None:
    min = re.search('\d{1,2}', update.effective_message.text)
    user = update.effective_user.username
    text = (
        f'Я добавил к твоему времени {min.group(0)} минут. А теперь выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    keyboard = [
            [
                InlineKeyboardButton("1", callback_data=str(1)),
                InlineKeyboardButton("2", callback_data=str(2)),
                InlineKeyboardButton("3", callback_data=str(3)),
            ],
            [
                InlineKeyboardButton("4", callback_data=str(4)),
                InlineKeyboardButton("5", callback_data=str(5)),
                InlineKeyboardButton("6", callback_data=str(6)),
            ],
            [
                InlineKeyboardButton("7", callback_data=str(7)),
                InlineKeyboardButton("8", callback_data=str(8)),
                InlineKeyboardButton("9", callback_data=str(9)),
            ],
            [
                InlineKeyboardButton("0", callback_data=str(0)),
                InlineKeyboardButton("Отмена", callback_data=str(stop_query)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 14, min.group(0))

    return DELETE


def error_answer(update: Update, context: CallbackContext) -> None:
    text = (
        f'Я не смог понять, сколько у тебя было удалений. Пожалуйста, выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    keyboard = [
            [
                InlineKeyboardButton("1", callback_data=str(1)),
                InlineKeyboardButton("2", callback_data=str(2)),
                InlineKeyboardButton("3", callback_data=str(3)),
            ],
            [
                InlineKeyboardButton("4", callback_data=str(4)),
                InlineKeyboardButton("5", callback_data=str(5)),
                InlineKeyboardButton("6", callback_data=str(6)),
            ],
            [
                InlineKeyboardButton("7", callback_data=str(7)),
                InlineKeyboardButton("8", callback_data=str(8)),
                InlineKeyboardButton("9", callback_data=str(9)),
            ],
            [
                InlineKeyboardButton("0", callback_data=str(0)),
                InlineKeyboardButton("Отмена", callback_data=str(stop_query)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)

    return DELETE


def error_order(update: Update, context: CallbackContext) -> None:
    text = (
        f'Ты присылаешь новый номер заказа. Пожалуйста, пришли сначала количество отмен по прошлому заказу, чтобы я мог посчитать твою статистику.'
    )
    keyboard = [
            [
                InlineKeyboardButton("1", callback_data=str(1)),
                InlineKeyboardButton("2", callback_data=str(2)),
                InlineKeyboardButton("3", callback_data=str(3)),
            ],
            [
                InlineKeyboardButton("4", callback_data=str(4)),
                InlineKeyboardButton("5", callback_data=str(5)),
                InlineKeyboardButton("6", callback_data=str(6)),
            ],
            [
                InlineKeyboardButton("7", callback_data=str(7)),
                InlineKeyboardButton("8", callback_data=str(8)),
                InlineKeyboardButton("9", callback_data=str(9)),
            ],
            [
                InlineKeyboardButton("0", callback_data=str(0)),
                InlineKeyboardButton("Отмена", callback_data=str(stop_query)),
            ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)

    return DELETE


def error_done(update: Update, context: CallbackContext) -> None:
    text = (
        f'Ты присылаешь новый номер заказа. Пожалуйста, пришли сначала фото чека. Не забывай это делать вовремя, иначе я неправильно считаю статистику :('
    )
    update.message.reply_text(text)

    return DONE


def done(update: Update, context: CallbackContext) -> None:
    #query = update.callback_query
    #query.answer()
    user = update.effective_user.username
    time = update.effective_message.date.strftime("%H:%M")
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 8, time)
    stat_check = worksheet.cell(val.row, 11).value
    stat_time = worksheet.cell(val.row, 12).value
    day_check = worksheet.cell(val.row, 17).value
    day_time = worksheet.cell(val.row, 18).value
    day_cash = worksheet.cell(val.row, 19).value
    text = (
        f'Заказ успешно закрыт. Твоя статистика за заказ:\n'
        f'Корзина: {stat_check}, Время на позицию: {stat_time}\n\n'
        f'Твоя статистика за день:\n'
        f'Корзина: {day_check}, Время на позицию: {day_time}, Ставка: {day_cash}р\n\n'
        f'Пересылай следующий заказ, как только придёт :)'
    )
    order = worksheet.cell(val.row, 2).value
    text_order = (
        f'Чек по заказу {order}:'
    )
    bot.send_message(CHECK_CHAT, text_order)
    update.message.forward(CHECK_CHAT)
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


def stop_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user = update.effective_user.username
    text = (
        f'Заказ отменён. Жду следующего ;)'
    )
    update.effective_message.reply_text(text)
    val = worksheet.findall(user)[-1]
    worksheet.update_cell(val.row, 10, "Отмена")

    return ConversationHandler.END


def stat(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.username
    val = worksheet.findall(user)[-1]
    day_check = worksheet.cell(val.row, 17).value
    day_time = worksheet.cell(val.row, 18).value
    day_cash = worksheet.cell(val.row, 19).value
    text = (
        f'Твоя статистика за день:\n'
        f'Корзина: {day_check}, Время на позицию: {day_time}, Ставка: {day_cash}р\n\n'
    )
    update.effective_message.reply_text(text)


# Подтверждение выдачи заказа
def close(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    order = re.search(r'\d{6}-\d{6}', update.effective_message.text)
    text = (
        f'Заказ выдан'
    )
    query.edit_message_text(text)
    val = worksheet.findall(order.group(0))[+1]
    worksheet.update_cell(val.row, 10, "Выдан")


def admin_reload(update: Update, context: CallbackContext) -> None:
    check = worksheet.cell(1, 23).value
    text = (
        f'Я добавил к твоему времени минут. А теперь выбери нужное количество на кнопке, или напиши количество удалений цифрой.'
    )
    if check == "1":
        order1 = worksheet.cell(2, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                ],
        ]
    elif check == "2":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                ],
        ]
    elif check == "3":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
        ]
    elif check == "4":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        order4 = worksheet.cell(5, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
                [
                    InlineKeyboardButton(order4, callback_data=str(order40)),
                ],
        ]
    elif check == "5":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        order4 = worksheet.cell(5, 22).value
        order5 = worksheet.cell(6, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
                [
                    InlineKeyboardButton(order4, callback_data=str(order40)),
                    InlineKeyboardButton(order5, callback_data=str(order50)),
                ],
        ]
    elif check == "6":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        order4 = worksheet.cell(5, 22).value
        order5 = worksheet.cell(6, 22).value
        order6 = worksheet.cell(7, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
                [
                    InlineKeyboardButton(order4, callback_data=str(order40)),
                    InlineKeyboardButton(order5, callback_data=str(order50)),
                    InlineKeyboardButton(order6, callback_data=str(order60)),
                ],
        ]
    elif check == "7":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        order4 = worksheet.cell(5, 22).value
        order5 = worksheet.cell(6, 22).value
        order6 = worksheet.cell(7, 22).value
        order7 = worksheet.cell(8, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
                [
                    InlineKeyboardButton(order4, callback_data=str(order40)),
                    InlineKeyboardButton(order5, callback_data=str(order50)),
                    InlineKeyboardButton(order6, callback_data=str(order60)),
                ],
                [
                    InlineKeyboardButton(order7, callback_data=str(order70)),
                ],
        ]
    elif check == "8":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        order4 = worksheet.cell(5, 22).value
        order5 = worksheet.cell(6, 22).value
        order6 = worksheet.cell(7, 22).value
        order7 = worksheet.cell(8, 22).value
        order8 = worksheet.cell(9, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
                [
                    InlineKeyboardButton(order4, callback_data=str(order40)),
                    InlineKeyboardButton(order5, callback_data=str(order50)),
                    InlineKeyboardButton(order6, callback_data=str(order60)),
                ],
                [
                    InlineKeyboardButton(order7, callback_data=str(order70)),
                    InlineKeyboardButton(order8, callback_data=str(order80)),
                ],
        ]
    elif check == "9":
        order1 = worksheet.cell(2, 22).value
        order2 = worksheet.cell(3, 22).value
        order3 = worksheet.cell(4, 22).value
        order4 = worksheet.cell(5, 22).value
        order5 = worksheet.cell(6, 22).value
        order6 = worksheet.cell(7, 22).value
        order7 = worksheet.cell(8, 22).value
        order8 = worksheet.cell(9, 22).value
        order9 = worksheet.cell(10, 22).value
        keyboard = [
                [
                    InlineKeyboardButton(order1, callback_data=str(order10)),
                    InlineKeyboardButton(order2, callback_data=str(order20)),
                    InlineKeyboardButton(order3, callback_data=str(order30)),
                ],
                [
                    InlineKeyboardButton(order4, callback_data=str(order40)),
                    InlineKeyboardButton(order5, callback_data=str(order50)),
                    InlineKeyboardButton(order6, callback_data=str(order60)),
                ],
                [
                    InlineKeyboardButton(order7, callback_data=str(order70)),
                    InlineKeyboardButton(order8, callback_data=str(order80)),
                    InlineKeyboardButton(order9, callback_data=str(order90)),
                ],
        ]
    if check == "0":
        bot.send_message(ADMIN_CHAT, text)
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(ADMIN_CHAT, text, reply_markup=reply_markup)


# Кот говорит мяу
def talk(update: Update, context: CallbackContext) -> None:
    random_sticker = lambda: random.choice(cat.sticker_cat)
    random_message = lambda: random.choice(cat.talk)
    stat = lambda: random.choice(['1','2','3'])
    if stat() == "1":
        update.message.reply_text(random_message())
    else:
        update.message.reply_sticker(sticker=random_sticker())


def callback_test(update, context):
    admin_reload(update, context)


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Слушает сообщения от всех и мявкает в ответ
    dispatcher.add_handler(MessageHandler(Filters.regex(cat.listen) & ~Filters.regex('\d{6}-\d{6}'), talk))

    # Слушает тапы по кнопке удаления
    dispatcher.add_handler(CallbackQueryHandler(close, pattern='^' + str(close) + '$'))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('stat', stat))
    dispatcher.add_handler(CommandHandler('test', callback_test))

    # Слушает чат сборки и собирает номера заказов
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('\d{6}-\d{6}') & ~Filters.chat(SBOR_CHAT), order_user)],
        states={
            DELETE: [
                MessageHandler(Filters.regex('^\d{,2}$')& ~Filters.regex('^[+]\d{,2}$') & ~Filters.regex('(Отмена|отмена|Отменяется|отменяется|Отменен|отменен|Отменён|отменён|Отменится|отменится)') & ~Filters.regex('\d{6}-\d{6}'), delete_answer),
                MessageHandler(Filters.text & ~Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('^[+]\d{,2}$'), error_answer),
                MessageHandler(Filters.regex('\d{6}-\d{6}'), error_order),
                MessageHandler(Filters.regex('^[+]\d{,2}$') & ~Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}'), add_min),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(1) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(2) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(3) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(4) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(5) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(6) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(7) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(8) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(9) + '$'),
                CallbackQueryHandler(delete_answer_query, pattern='^' + str(0) + '$'),
                CallbackQueryHandler(stop_query, pattern='^' + str(stop_query) + '$'),
            ],
            DONE: [
                MessageHandler(Filters.photo, done),
                MessageHandler(Filters.regex('\d{6}-\d{6}'), error_done),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('(Отмена|отмена|Отменяется|отменяется|Отменен|отменен|Отменён|отменён|Отменится|отменится)'), stop)],
    )


    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
