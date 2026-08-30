"""Local Polling Runner for Development"""

import asyncio

from app.bot.telegram import ADMIN, bot
from app.logger import log


async def main() -> None:
    """Removes webhook and starts long polling."""
    log.info("Starting bot in local polling mode...")
    await bot.remove_webhook()

    me = await bot.get_me()
    log.info("Bot authenticated as @%s (ID: %s)", me.username, me.id)

    if ADMIN:
        try:
            await bot.send_message(
                chat_id=ADMIN,
                text=f"🤖 Bot @{me.username} started in polling mode.",
            )
        except Exception as exc:
            log.warning("Could not send startup message to admin: %s", exc)

    log.info("Listening for updates...")
    await bot.polling(non_stop=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped by user.")
