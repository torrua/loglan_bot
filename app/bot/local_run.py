import asyncio
import os

from app.bot import bot

admin = os.getenv("TELEGRAM_ADMIN_ID")

if __name__ == "__main__":

    async def main():
        await bot.remove_webhook()
        await bot.send_message(chat_id=admin, text=await bot.get_me())
        await bot.polling(none_stop=True)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
