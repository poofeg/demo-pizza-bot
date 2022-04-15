import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

import gspread_asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
SERVICE_ACCOUNT_FILENAME = os.getenv('SERVICE_ACCOUNT_FILENAME')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dataclass
class MenuItem:
    name: str
    photo: str


menu: list[MenuItem] = []
ws_orders: Optional[gspread_asyncio.AsyncioGspreadWorksheet] = None


class Form(StatesGroup):
    welcome = State()
    phone_number = State()
    menu = State()
    order = State()


def get_creds() -> Credentials:
    # To obtain a service account JSON file, follow these steps:
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILENAME)
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


async def init_gspread() -> None:
    global ws_orders
    if ws_orders:
        return

    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    ss = await agc.open_by_key(SPREADSHEET_ID)

    ws_menu = await ss.get_worksheet(1)
    ws_values = await ws_menu.get_values()
    for row in ws_values[1:]:
        item = MenuItem(name=row[0], photo=row[1])
        menu.append(item)

    ws_orders = await ss.get_worksheet(0)


async def send_welcome(message: types.Message) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Отправить контакт', request_contact=True))
    await message.answer(
        f'Здравствуйте, {message.from_user.first_name}! Ваш номер телефона?',
        reply_markup=markup
    )
    await Form.phone_number.set()


async def send_menu(message: types.Message) -> None:
    await Form.order.set()
    markup = types.ReplyKeyboardRemove()
    await message.answer('*Меню*', parse_mode='MarkdownV2', reply_markup=markup)

    for item in menu:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton('Заказать 1 порцию', callback_data=f'{item.name}|1')
            ],
            [
                types.InlineKeyboardButton('2', callback_data=f'{item.name}|2'),
                types.InlineKeyboardButton('3', callback_data=f'{item.name}|3'),
                types.InlineKeyboardButton('4', callback_data=f'{item.name}|4'),
                types.InlineKeyboardButton('5', callback_data=f'{item.name}|5'),
            ],
        ])
        await message.answer_photo(item.photo, item.name, reply_markup=markup)


@dp.message_handler(state='*', commands=['start', 'help'])
async def process_start(message: types.Message) -> None:
    await send_welcome(message)


@dp.callback_query_handler(state=Form.order)
async def process_order(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        phone_number: str = data['phone_number']
    logging.info('order %s tel %s', callback_query.data, phone_number)
    product_name, quantity = callback_query.data.split('|')
    await ws_orders.append_row([
        datetime.now().isoformat(),
        callback_query.from_user.username,
        callback_query.from_user.first_name,
        callback_query.from_user.last_name,
        phone_number,
        product_name,
        quantity,
    ])
    await Form.menu.set()
    answer = f'Спасибо за заказ! Вы заказали: {product_name} x {quantity}. Мы скоро свяжемся с вами.'
    await callback_query.answer(answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Новый заказ'))
    await bot.send_message(callback_query.from_user.id, answer, reply_markup=markup)
    await bot.send_message(ADMIN_CHAT_ID, f'Новый заказ: {product_name} x {quantity}')


@dp.message_handler(state=Form.phone_number, content_types=types.ContentType.CONTACT)
async def process_contact(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['phone_number'] = message.contact.phone_number
    await send_menu(message)


@dp.message_handler(state=Form.phone_number, regexp=r'^(?:\+7|8)?\d{10}$')
async def process_phone_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await send_menu(message)


@dp.message_handler(state=Form.menu, content_types=types.ContentType.ANY)
async def process_menu(message: types.Message) -> None:
    await send_menu(message)


@dp.message_handler(state=Form.order, content_types=types.ContentType.ANY)
async def process_invalid_order(message: types.Message) -> None:
    await send_menu(message)


@dp.message_handler(state='*', content_types=types.ContentType.ANY)
async def process_welcome(message: types.Message) -> None:
    await send_welcome(message)


async def handler(event: dict[str, Any], context: Any) -> dict:
    """Yandex.Cloud functions handler."""
    logging.getLogger().setLevel(logging.DEBUG)
    if event['httpMethod'] == 'POST':
        update = json.loads(event['body'])
        logging.debug('Update: %s', update)
        Dispatcher.set_current(dp)
        Bot.set_current(dp.bot)
        update = types.Update.to_object(update)
        await init_gspread()
        await dp.process_update(update)
        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}


def run() -> None:
    logging.basicConfig(level=logging.DEBUG)

    async def on_startup(dispatcher: Dispatcher) -> None:
        await init_gspread()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)


if __name__ == '__main__':
    run()
