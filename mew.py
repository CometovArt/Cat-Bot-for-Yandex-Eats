from telegram import Update
from telegram.ext import CallbackContext

import random
import pathlib

import cat


# Кот говорит мяу
def talk(update: Update, context: CallbackContext) -> None:
    random_message = lambda: random.choice(cat.talk)
    random_voice = lambda: random.choice(cat.voice)
    random_sticker = lambda: random.choice(cat.sticker)

    stat = lambda: random.choice(['1','2','3'])

    if stat() == "1":
        update.message.reply_text(random_message())

    elif stat() == "2":
        update.message.reply_voice(open(pathlib.Path('voice', random_voice()), 'rb'))

    else:
        update.message.reply_sticker(sticker=random_sticker())


# Кот шипит
def woof(update: Update, context: CallbackContext) -> None:
    random_voice = lambda: random.choice(cat.shh)
    update.message.reply_voice(open(random_voice(), 'rb'))
