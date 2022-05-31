from telegram import Update
from telegram.ext import CallbackContext

import random
import pathlib

import cat


# Кот говорит мяу
async def talk(update: Update, context: CallbackContext) -> None:
    random_message = lambda: random.choice(cat.talk)
    random_voice = lambda: random.choice(cat.voice)
    random_sticker = lambda: random.choice(cat.sticker)

    stat = lambda: random.choice(['1','1','3'])

    if stat() == "1":
        await update.message.reply_text(random_message())

    elif stat() == "2":
        await update.message.reply_voice(open(pathlib.Path('voice', random_voice()), 'rb'))

    else:
        await update.message.reply_sticker(sticker=random_sticker())


# Кот шипит
async def woof(update: Update, context: CallbackContext) -> None:
    random_voice = lambda: random.choice(cat.shh)
    await update.message.reply_voice(open(random_voice(), 'rb'))
