from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler

from config import statsheet, leadersheet, SETTING, SETTING_NAME_DONE, SETTING_LEADERBOARD_ANSWER
from keyboards import keyboard_setting


async def setting_user(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    try:
        query.data
    except:
        update = update.message
    else:
        await query.answer()
        update = query.message
    text = (
        f'Здесь ты можешь настроить бота под себя.'
    )
    await update.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_setting))

    return SETTING


async def setting_edit_name(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    text = (
        f'Как тебя зовут?'
    )
    keyboard_setting_back = [[InlineKeyboardButton("Назад", callback_data=str('setting_user'))]]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard_setting_back))

    return SETTING_NAME_DONE


async def setting_edit_name_error(update: Update, context: CallbackContext) -> None:
    text = (
        f'Не понял :('
    )
    await update.message.reply_text(text)

    return SETTING_NAME_DONE


async def setting_edit_name_done(update: Update, context: CallbackContext) -> None:
    update = update.message
    name = update.text
    
    try:
        statsheet.find(name)
    except:
        user = update.from_user.username
        text = (
            f'Приятно познакомиться, {name}'
        )
        await update.reply_text(text)
        scan = statsheet.find(user) # ищем последний заказ
        statsheet.update_cell(2, scan.col, name)
        RETURNED = ConversationHandler.END
    else: 
        text = (
            f'Такое имя уже используется. Пожалуйста, напиши другое'
        )
        await update.reply_text(text)
        RETURNED = SETTING_NAME_DONE

    return RETURNED


async def setting_leaderboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user = query.message.chat.username
    
    text = (
        f'Если ты не хочешь, чтобы твои результаты учитывались '
        f'в рейтингах, то можешь это сделать по кнопке ниже.\n\n'
        f'_Исключение из рейтингов запретит публикацию твоих результатов _'
        f'_в ежедневной статистике, а так же отключит все остальные рейтинговые системы._'
    )
    
    scan = leadersheet.find(user)
    val = leadersheet.cell(scan.row, scan.col-1).value
    
    if val == '0':
        toggle = 'Включить участие в рейтинах'
        toggle_callback = 'leaderboard_on'
    else:
        toggle = 'Выключить участие в рейтинах'
        toggle_callback = 'leaderboard_off'
    
    keyboard_setting_leaderboard = [
        [InlineKeyboardButton(f'{toggle}', callback_data=str(toggle_callback))],
        [InlineKeyboardButton("Назад", callback_data=str('setting_user'))],
    ]
    
    await query.message.reply_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard_setting_leaderboard))

    return SETTING_LEADERBOARD_ANSWER


async def setting_leaderboard_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    user = query.message.chat.username
    scan = leadersheet.find(user)
    
    toggle_callback = query.data
    
    if toggle_callback == 'leaderboard_on':
        text = 'Участие в рейтингах успешно включено ✨'
        leadersheet.update_cell(scan.row, scan.col-1, '1')
    else:
        text = 'Участие в рейтингах успешно отключено 😿'
        leadersheet.update_cell(scan.row, scan.col-1, '0')

    await query.message.reply_text(text, parse_mode='markdown')

    return ConversationHandler.END