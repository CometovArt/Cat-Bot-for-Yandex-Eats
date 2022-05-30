from telegram import InlineKeyboardButton

keyboard_change = [
        [
            InlineKeyboardButton("Изменить кол-во удалений", callback_data=str('delete_back')),
        ],
]


keyboard_delete = [
        [
            InlineKeyboardButton("1", callback_data=str('1')),
            InlineKeyboardButton("2", callback_data=str('2')),
            InlineKeyboardButton("3", callback_data=str('3')),
        ],
        [
            InlineKeyboardButton("4", callback_data=str('4')),
            InlineKeyboardButton("5", callback_data=str('5')),
            InlineKeyboardButton("6", callback_data=str('6')),
        ],
        [
            InlineKeyboardButton("7", callback_data=str('7')),
            InlineKeyboardButton("8", callback_data=str('8')),
            InlineKeyboardButton("9", callback_data=str('9')),
        ],
        [
            InlineKeyboardButton("+ позиция", callback_data=str('add_pos')),
            InlineKeyboardButton("Отмена заказа", callback_data=str('order_cancel')),
        ],
]

keyboard_name = [
        [
            InlineKeyboardButton("Изменить имя", callback_data=str('setting_edit_name')),
        ],
]