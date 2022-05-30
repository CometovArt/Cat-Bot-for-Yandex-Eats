# Автозапуск бота лежит в /lib/systemd/system/catbot.service
# Рестарт бота systemctl restart catbot.service

import logging
import pathlib

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, PicklePersistence

# Импорт файла с репликами кота
import cat
from admin import admin_done
from config import bot, SBOR_CHAT, DEV_CHAT, TOKEN, LOGFILE, DELETE, ADD, DONE
from mew import talk, woof
from errors import error_answer, error_order, error_done, error_add, error_handler
from orders import order_user, delete_answer, add_pos, add_answer, delete_back, add_min, done, done_photo, order_cancel
from command import start, stat, callback_reload, id, test, test_voice


# Логинг логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = LOGFILE)
logger = logging.getLogger(__name__)


bot.send_message(DEV_CHAT, "Бот запущен")


def main() -> None:
    persistence = PicklePersistence(filename=pathlib.Path('service', 'conversation_cache'))
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
    dispatcher.add_handler(CommandHandler('test', test))

    # Слушает чат сборки и собирает номера заказов
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('\d{6}-\d{6}') & ~Filters.chat(SBOR_CHAT), order_user)],
        states={
            DELETE: [
                MessageHandler(Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('^[+]\d{,2}$'), delete_answer),
                MessageHandler(Filters.text & ~Filters.regex('(Отмена|отмена|Отменяется|отменяется|Отменен|отменен|Отменён|отменён|Отменится|отменится)') & ~Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}') & ~Filters.regex('^[+]\d{,2}$'), error_answer),
                MessageHandler(Filters.regex('\d{6}-\d{6}'), error_order),
                MessageHandler(Filters.regex('^[+]\d{,2}$') & ~Filters.regex('^\d{,2}$') & ~Filters.regex('\d{6}-\d{6}'), add_min),
                CallbackQueryHandler(delete_answer, pattern='^' + str('\d{1}') + '$'),
                CallbackQueryHandler(add_pos, pattern='^' + str('add_pos') + '$'),
                CallbackQueryHandler(order_cancel, pattern='^' + str('order_cancel') + '$'),
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
        fallbacks=[MessageHandler(Filters.regex('(Отмена|отмена|Отменяется|отменяется|Отменен|отменен|Отменён|отменён|Отменится|отменится)'), order_cancel)],
        name = 'conversationhandler',
        persistent = True,
    )


    dispatcher.add_handler(CallbackQueryHandler(admin_done, pattern='^' + str('\d{6}') + '$'))
    dispatcher.add_error_handler(error_handler)

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
