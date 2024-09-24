import aiohttp
import asyncio
import logging
import schedule
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand
from config import TOKEN

bot = Bot(token=TOKEN)
router = Dispatcher()

# Set up logging to track what's happening
logging.basicConfig(filename='crypto_monitoring.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
        
monitoring = False
chat_id = None
selected_crypto = None

async def get_crypto_price(symbol):
    url = f'https://api.binance.com/api/v3/avgPrice?symbol={symbol}USDT'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json_response = await response.json()
                price = json_response.get('price')
                if price:
                    return f'Цена {symbol} на {time.ctime()}: {price}'
                else:
                    return f'Не удалось получить цену для {symbol}'
    except Exception as e:
        logging.error(f'Ошибка при получении цены {symbol}: {e}')
        return 'Ошибка запроса к Binance API'

async def monitor_crypto_price(symbol):
    global monitoring
    logging.info(f'Начинаем следить за {symbol}')
    while monitoring:
        try:
            message = await get_crypto_price(symbol)
            logging.info(f'Новая цена {symbol}: {message}')
            await bot.send_message(chat_id, message)
        except Exception as e:
            logging.error(f'Ошибка в мониторинге {symbol}: {e}')
        await asyncio.sleep(10)
    logging.info(f'Мониторинг {symbol} остановлен')

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}!')

@router.message(Command('btc'))
async def btc(message: Message):
    global chat_id, monitoring, selected_crypto
    chat_id = message.chat.id
    selected_crypto = 'BTC'
    if not monitoring:
        monitoring = True
        await message.answer("Начинаю следить за Bitcoin!")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Я уже слежу за чем-то!")

@router.message(Command('eth'))
async def eth(message: Message):
    global chat_id, monitoring, selected_crypto
    chat_id = message.chat.id
    selected_crypto = 'ETH'
    if not monitoring:
        monitoring = True
        await message.answer("Начинаю следить за Ethereum!")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Я уже слежу за чем-то!")

@router.message(Command('ltc'))
async def ltc(message: Message):
    global chat_id, monitoring, selected_crypto
    chat_id = message.chat.id
    selected_crypto = 'LTC'
    if not monitoring:
        monitoring = True
        await message.answer("Начинаю следить за Litecoin!")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Я уже слежу за чем-то!")

@router.message(Command('stop'))
async def stop(message: Message):
    global monitoring
    if monitoring:
        monitoring = False
        await message.answer("Мониторинг остановлен.")
    else:
        await message.answer("Мониторинг уже остановлен!")

def periodic_report():
    loop = asyncio.get_event_loop()
    if selected_crypto:
        message = loop.run_until_complete(get_crypto_price(selected_crypto))
        loop.run_until_complete(bot.send_message(chat_id, f'Периодический отчет: {message}'))

def scheduler():
    schedule.every(10).minutes.do(periodic_report)
    while True:
        schedule.run_pending()
        time.sleep(1)

async def on_startup():
    await bot.set_my_commands([
        BotCommand(command="/start", description='Запустить бота'),
        BotCommand(command="/btc", description='Следить за Bitcoin'),
        BotCommand(command="/eth", description='Следить за Ethereum'),
        BotCommand(command="/ltc", description='Следить за Litecoin'),
        BotCommand(command="/stop", description='Остановить мониторинг'),
    ])
    logging.info("Бот запущен!")

async def main():
    await on_startup()
    asyncio.create_task(asyncio.to_thread(scheduler))  # Запускаем планировщик
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
