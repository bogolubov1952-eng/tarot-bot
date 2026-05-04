import asyncio
import threading
import os
from aiohttp import web
from bot import dp, bot

async def handle(request):
    return web.Response(text="Bot is running")

async def run_web_server():
    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def start_bot():
    await bot.delete_webhook()
    await dp.start_polling(bot)

def run_bot():
    asyncio.run(start_bot())

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    asyncio.run(run_web_server())
