import asyncio
from pyrogram import Client

api_id = 9545469
api_hash = "004d9e767672f364cbae700905837819"


async def main():
    async with Client("cometovtest", api_id, api_hash) as app:
        await app.send_message("me", "Greetings from **Pyrogram**!")


asyncio.run(main())

#systemctl daemon-reload && systemctrl start catbot.service