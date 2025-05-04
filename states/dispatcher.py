from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup
from yoomoney import Client
from config.config import YOO_TOKEN

dp = Dispatcher()
client = Client(YOO_TOKEN)

class UserState(StatesGroup):
    waiting_for_media_1 = State()
    waiting_for_media_2 = State()
    waiting_for_media_3 = State()
    waiting_for_description = State()
    waiting_for_price = State()
    mail = State()
    password = State()
    idle = State()

class YooState(StatesGroup):
    num_account = State()
    idle = State()

class AdminState(StatesGroup):
    text_of_send = State()
    waiting_for_id = State()
    idle = State()