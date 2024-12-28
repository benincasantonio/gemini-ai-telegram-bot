from telegram.ext import ApplicationBuilder
import asyncio

async def set_telegram_secret_token():
    telegram_app = ApplicationBuilder().token(
    "964027989:AAHTXVzgbavAN2PSche5OG93qwoHsikCLe8"
    ).build()

    response = await telegram_app.bot.setWebhook(secret_token="wD5CxgmmR7_yra8RWHg-N6q_KKLxuK", url="https://router-4foqoal5na-uc.a.run.app/webhook" )
    print('Webhook set successfully', response)


asyncio.run(set_telegram_secret_token())