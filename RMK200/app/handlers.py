from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart 
from aiogram.types import Message
from app.keyboards import keyboard1

import time
import aiohttp
import logging
import asyncio

router=Router()
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
                    return f'Стоимость {symbol} на {time.ctime()}, {price}'
                else:
                    return f'Не удалось получить цену {symbol}'
    except Exception as e:
        logging.error(f'Ошибка при запросе {symbol}: {e}')
        return 'Ошибка запроса к Binance API'


async def monitor_crypto_price(symbol):
    global monitoring
    logging.info(f'Начат мониторинг {symbol}')
    while monitoring:
        try:
            message = await get_crypto_price(symbol)
            logging.info(f'Изменение цены {symbol}: {message}')
            await router.send_message(chat_id, message)
        except Exception as e:
            logging.error(f'Ошибка мониторинга {symbol}: {e}')
        await asyncio.sleep(10)
    logging.info(f'Мониторинг {symbol} остановлен')

@router.message(CommandStart())
async def Skyfall(message:Message):
    await message.reply("heloo goa ", reply_markup=keyboard1)

    
@router.message(Command ("help"))
async def Skyll(message:Message):
    await message.reply("нужные вам команды  /ltc,/eth,/bit")


@router.message(Command("bit"))
async def faceitall(message:Message):
    global monitoring,chat_id,selected_crypto
    chat_id=message.chat.id
    selected_crypto='BTC'
    if  monitoring == False:
        monitoring==True
        await message.answer("Начало мониторинга Bitcoin")
        asyncio.create_task(monitor_crypto_price(selected_crypto))
    else:
        await message.answer("Мониторинг уже запущен!")
