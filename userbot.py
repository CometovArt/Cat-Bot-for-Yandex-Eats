from pyrogram import Client, filters

FOODFOX = 289312219
CATBOT = 5301183609


# Сборщик _1

app_1 = Client("misha_1")

@app_1.on_message(filters.user(FOODFOX) & filters.Regex('\d{6}-\d{6}'))
async def pars_order(client, message):
    await app_1.send_message(CATBOT, message)
    
app_1.run()


# Сборщик _2

app_2 = Client("olga_2")

@app_1.on_message(filters.user(FOODFOX) & filters.Regex('\d{6}-\d{6}'))
async def pars_order(client, message):
    await app_1.send_message(CATBOT, message)
    
app_2.run()