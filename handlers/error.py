from aiogram import types, Router
from keyboards.keyboard import *

router = Router()

@router.message()
async def error_handler(message: types.Message):
    await message.answer('К сожалению такой команды нет :(')