import asyncio
import threading
from aiohttp import web
from bot import dp, bot  # Импортируем твоего бота из файла bot.py

# Создаём простой сайт-заглушку
async def handle(request):
    return web.Response(text="Бот работает")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

# Запускаем бота в отдельном потоке
async def start_bot():
    await bot.delete_webhook()
    await dp.start_polling(bot)

def run_bot():
    asyncio.run(start_bot())

if __name__ == "__main__":
    import os
    # Запускаем бота в фоне
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    # Запускаем веб-сервер
    asyncio.run(run_web_server())