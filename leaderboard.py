from telegram import Update
from telegram.ext import CallbackContext

from config import bot, leadersheet, DEV_CHAT, SBOR_CHAT


async def dayleader(context: CallbackContext):
    val = leadersheet.get('D25:I38')
    
    user_list = []

    for i in range(3, int(val[2][1]) + 3):
        try:
            user_list.append(f'*{val[i][1]} —* 🛒 {val[i][2]} | ⏳ {val[i][3]} | 💵 {val[i][4]} | 📦 {val[i][5]}\n')
        except:
            i
    
    text = (
            f'*Лучший сборщик сегодня:* [{val[0][1]}](t.me/{val[0][0]})\n\n'
            f'🛒 Корзина: *{val[0][2]}*, ⏳ На позицию: *{val[0][3]}*,\n'
            f'💵 Ставка: *{val[0][4]}*, 📦 Заказов: *{val[0][5]}*\n\n\n'
            f'Статистика всех остальных:\n\n'
            f'{"".join(user_list)}\n\n'
            f'_Всем хорошего вечера, увидимся завтра!_\n\n' 
            )
    
    await bot.send_message(SBOR_CHAT, text, parse_mode='markdown', disable_web_page_preview=True)
    
async def dayleaders(update: Update, context: CallbackContext):
    val = leadersheet.get('D25:I38')
    
    user_list = []

    for i in range(3, int(val[2][1]) + 3):
        try:
            user_list.append(f'*{val[i][1]} —* 🛒 {val[i][2]} | ⏳ {val[i][3]} | 💵 {val[i][4]} | 📦 {val[i][5]}\n')
        except:
            i
    
    text = (
            f'*Лучший сборщик сегодня:* [{val[0][1]}](t.me/{val[0][0]})\n\n'
            f'🛒 Корзина: *{val[0][2]}*, ⏳ На позицию: *{val[0][3]}*,\n'
            f'💵 Ставка: *{val[0][4]}*, 📦 Заказов: *{val[0][5]}*\n\n\n'
            f'Статистика всех остальных:\n\n'
            f'{"".join(user_list)}\n\n'
            f'_Всем хорошего вечера, увидимся завтра!_\n\n' 
            )
    
    await bot.send_message(SBOR_CHAT, text, parse_mode='markdown', disable_web_page_preview=True)