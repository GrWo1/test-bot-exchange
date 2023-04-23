import os
import logging
import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from keyboards import keyboard


load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_TOKEN = os.getenv('CHAT_ID')
OPEN_WEATHER_TOKEN = os.getenv('OPEN_WEATHER_TOKEN')
EXCHANGE_RATES_TOKEN = os.getenv('EXCHANGE_RATES_TOKEN')


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    number = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """ Привествие после запуска бота."""
    await message.answer(
        text='Здравствуйте! Помогу чем смогу...',
        reply_markup=keyboard,
        parse_mode='HTML',
    )


@dp.message_handler(lambda message: message.text == 'Конвертировать валюту')
async def get_exchange(message: types.Message):
    """
    Функция подсказывает пользователю формат ввода валют для конвертации.
    Ожидает пока пользователь не введет данные.
    """
    await message.answer(
        text='Введите количество и валюты из какой в какую через пробел.\n'
             'Пример: 10 USD RUB',
    )
    await message.delete()
    await Form.number.set()


@dp.message_handler(state=Form.number)
async def exchange(message: types.Message):
    """ Функция конвертации валюты."""
    try:
        amount, from_s, to_s = message.text.split()
        amount = int(amount)
        from_s = from_s.upper()
        to_s = to_s.upper()
        url = f'https://api.apilayer.com/exchangerates_data/convert?to={to_s}&from={from_s}&amount={amount}'
        payload = {}
        headers= {
          "apikey": EXCHANGE_RATES_TOKEN
        }
        response = requests.request("GET", url, headers=headers, data = payload).json()
        result = round(response.get('result'), 2)
        await message.answer(text=f'{amount} {from_s} = {result} {to_s} ')
    except ValueError:
        await message.answer('Ошибка ввода данных')
    except TypeError:
        await message.answer('Неверный формат валюты')


@dp.message_handler(lambda message: message.text == 'Получить котика 🐈')
async def get_cat(message: types.Message):
    """ Функция получения рандомного фото кота."""
    response = requests.get(url='https://api.thecatapi.com/v1/images/search').json()
    random_cat = response[0].get('url')
    await message.delete()
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=random_cat,
    )


@dp.message_handler(lambda message: message.text == 'Температура на улице')
async def get_weather(message: types.Message):
    """ Функция получения погоды на основе IP-адреса устройства."""
    address = 'https://ipinfo.io/json'
    response = requests.get(url=address).json()
    lat, lon = response['loc'].split(',')
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPEN_WEATHER_TOKEN,
        'units': 'metric',
    }
    address = 'https://api.openweathermap.org/data/2.5/weather?'
    response = requests.get(url=address, params=params).json()
    response = response.get('main')
    temp = round(response['temp'])
    await message.delete()
    await message.answer(text=f'Температура на улице {temp} ℃')


@dp.message_handler(lambda message: message.text == 'Показать мой IP')
async def get_ip_address(message: types.Message):
    """ Функция демонстрации IP-адреса"""
    address = 'https://ipinfo.io/json'
    response = requests.get(url=address).json()
    ip_address = response['ip']
    await message.delete()
    await message.answer(text=f'Ваш ip-адрес - {ip_address}')


if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True,  # Игнорировать все сообщения в оффлайн режиме
    )
