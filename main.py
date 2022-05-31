# API https://github.com/python-telegram-bot/python-telegram-bot
# Гайд по регулярным выражениям https://habr.com/ru/post/349860/
# Автозапуск бота лежит в /lib/systemd/system/catbot.service
# Рестарт бота systemctl restart catbot.service

import pathlib

from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler, ConversationHandler, PicklePersistence
)

import cat
from mew import talk, woof
from admin import admin_done

from config import (
    startmessage, TOKEN, 
    ORDER_DELETE, ORDER_ADD, ORDER_DONE, 
    SETTING_NAME, SETTING_NAME_DONE,
    )

from errors import (
    error_answer, 
    error_order, 
    error_done, 
    error_add, 
    error_handler,
    )

from orders import (
    order_user, delete_answer, 
    add_pos, add_answer, 
    delete_back, add_min, 
    done, done_photo, 
    order_cancel, order_close,
    )

from command import (
    start, stat, callback_reload, 
    getid, test, test_voice,
    )

from setting import (
    setting_user, setting_edit_name, 
    setting_edit_name_done, setting_edit_name_error,
    )


def main() -> None:
    
    # Коннект к API бота
    # Токен берётся из config.py
    # persistence - сохранение ConversationHandler
    ap = (
        Application.builder()
        .token(TOKEN)
        .persistence(
            PicklePersistence(
                filepath = pathlib.Path('service', 'conversation_cache')
                )
            )
        .build()
    )
    
    # Планировщик стартового сообщения
    job_queue = ap.job_queue
    job_queue.run_once(startmessage, 1)
    
    
    # Слушает сообщения от всех и мявкает в ответ
    # Фразы берёт из cat.py
    ap.add_handler(
        MessageHandler(
            filters.Regex(cat.listen_talk) 
            & ~filters.Regex('\d{6}-\d{6}') 
            & ~filters.Regex('([Я,я]ндекс|[Ф,ф]удфокс)') 
            & ~filters.ChatType.CHANNEL, 
            talk
            )
        )
    
    # Слушает сообщения от всех и гавкает в ответ
    # Фразы берёт из cat.py
    ap.add_handler(
        MessageHandler(
            filters.Regex(cat.listen_woof) 
            & ~filters.Regex('\d{6}-\d{6}'), 
            woof
            )
        )

    # Основные команды бота
    ap.add_handler(CommandHandler('start', start))
    ap.add_handler(CommandHandler('stat', stat))
    ap.add_handler(CommandHandler('reload', callback_reload))
    # Тестовые команды бота
    ap.add_handler(CommandHandler('id', getid))
    ap.add_handler(CommandHandler('test_voice', test_voice))
    ap.add_handler(CommandHandler('test', test))


    # Меню настроек
    # states определяют на какие хэндлеры реагирует бот
    setting_handler = ConversationHandler(
        entry_points = [CommandHandler('setting', setting_user)],
        states = {
            SETTING_NAME: [
                CallbackQueryHandler(setting_edit_name, pattern='^' + str('setting_edit_name') + '$'),
            ],
            SETTING_NAME_DONE: [
                MessageHandler(
                    filters.Regex('\w{3,8}') 
                    & ~filters.Regex('\w{9,}') 
                    & ~filters.Regex('\W'), 
                    setting_edit_name_done
                    ),
                MessageHandler(
                    (
                        ~filters.Regex('\w{3,8}')
                        | filters.Regex('\w{9,}')
                        | filters.Regex('\W')
                        ), 
                    setting_edit_name_error
                    ),
            ],
        },
        fallbacks = [
            MessageHandler(filters.Regex('^[О,о]тмен'), order_cancel),
            MessageHandler(filters.Regex('^[З,з]акр'), order_close),
            ],
    )
    

    # Слушает личку и запускает меню заказа
    order_handler = ConversationHandler(
        entry_points = [MessageHandler(
            filters.Regex('\d{6}-\d{6}') 
            & filters.ChatType.PRIVATE, 
            order_user
            )],
        states = {
            ORDER_DELETE: [
                MessageHandler(
                    filters.Regex('^\d{,2}$') 
                    & ~filters.Regex('\d{6}-\d{6}') 
                    & ~filters.Regex('^[+]\d{,2}$')
                    , delete_answer
                    ),
                MessageHandler(
                    filters.TEXT 
                    & ~filters.Regex('(^[О,о]тмен|^[З,з]акр)') 
                    & ~filters.Regex('^\d{,2}$') 
                    & ~filters.Regex('\d{6}-\d{6}') 
                    & ~filters.Regex('^[+]\d{,2}$'), 
                    error_answer
                    ),
                MessageHandler(filters.Regex('\d{6}-\d{6}'), error_order),
                MessageHandler(
                    filters.Regex('^[+]\d{,2}$') 
                    & ~filters.Regex('^\d{,2}$') 
                    & ~filters.Regex('\d{6}-\d{6}'), 
                    add_min
                    ),
                CallbackQueryHandler(delete_answer, pattern='^' + str('\d{1}') + '$'),
                CallbackQueryHandler(add_pos, pattern='^' + str('add_pos') + '$'),
                CallbackQueryHandler(order_cancel, pattern='^' + str('order_cancel') + '$'),
                MessageHandler(filters.PHOTO, done_photo),
            ],
            ORDER_ADD: [
                MessageHandler(
                    filters.Regex('^\d{,2}$') 
                    & ~filters.Regex('\d{6}-\d{6}') 
                    & ~filters.Regex('^[+]\d{,2}$')
                    & ~filters.Regex('(^[О,о]тмен|^[З,з]акр)'),
                    add_answer
                    ),
                MessageHandler(~filters.Regex('^\d{,2}$'), error_add),
                CallbackQueryHandler(delete_back, pattern='^' + str('delete_back') + '$'),
            ],
            ORDER_DONE: [
                MessageHandler(filters.PHOTO, done),
                MessageHandler(filters.Regex('\d{6}-\d{6}'), error_done),
                CallbackQueryHandler(delete_back, pattern='^' + str('delete_back') + '$'),
            ],
        },
        fallbacks = [
            MessageHandler(filters.Regex('^[О,о]тмен'), order_cancel),
            MessageHandler(filters.Regex('^[З,з]акр'), order_close),
            ],
        name = 'conversationhandler',
        persistent = True,
    )
        
    # Обработчик для админки
    ap.add_handler(CallbackQueryHandler(admin_done, pattern='^' + str('\d{6}') + '$'))
    
    # Обработчик ошибок
    ap.add_error_handler(error_handler)

    # Обработчик ConversationHandler
    ap.add_handler(setting_handler)
    ap.add_handler(order_handler)

    ap.run_polling(stop_signals=None)


if __name__ == '__main__':
    main()