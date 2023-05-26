from telegram import Bot

from library_service_api import settings


async def send_notification_to_telegram(
    token=settings.TELEGRAM_BOT_TOKEN,
    chat_id=settings.TELEGRAM_CHAT_ID,
    msg=None,
):
    bot = Bot(token=token)
    await bot.sendMessage(chat_id=chat_id, text=msg)
