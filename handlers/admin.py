from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from aiogram.filters import BaseFilter
from keyboards.keyboard import *
from states.dispatcher import AdminState
import aiosqlite, asyncio

router = Router()

ADMIN_ID = '2090971605'
admin_ids = [2090971605, 6137325838]

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admin_ids
    
@router.message(F.text == '/admin', IsAdmin())
async def admin_panel(message: types.Message):
    await message.answer('Выберите действие', reply_markup=admin_keyboard)

@router.callback_query(F.data == 'send')
async def send_news(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.text_of_send)
    await callback.message.answer('Введите сообщение которое хотите разослать')

@router.message(AdminState.text_of_send)
async def send_news_2(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    user_ids = await cursor.execute('SELECT user_id FROM users')
    user_ids = await user_ids.fetchall()
    for user_id in user_ids:
        await message.bot.send_message(user_id[0], data['text'])
    
    await message.answer('Рассылка выполнена', reply_markup=back_keyboard)
    await state.set_state(AdminState.idle)
    await state.clear()
    await cursor.close()
    await connect.close()

@router.callback_query(F.data == 'amount_user')
async def amount_user(callback: types.CallbackQuery):
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    user_ids = await cursor.execute('SELECT user_id FROM users')
    user_ids = await user_ids.fetchall()
    ads = await cursor.execute('SELECT token_ad FROM ads')
    ads = await ads.fetchall()
    await callback.message.answer(f'Пользователей в боте: {len(user_ids)}\n\nКоличество доступных объявлений: {len(ads)}', reply_markup=back_keyboard)
    await cursor.close()
    await connect.close()

@router.callback_query(F.data == 'amount_rub')
async def amount_user(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_for_id)
    await callback.message.answer('Введите id пользователя')

@router.message(AdminState.waiting_for_id)
async def select_id(message: types.Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    user_id = int(data['id'])
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    user_sum = await cursor.execute('SELECT sum FROM users WHERE user_id = ?', (user_id,))
    user_sum = await user_sum.fetchone()
    if user_sum == None:
        await message.answer('Такого пользователя нет в базе данных', reply_markup=back_keyboard)
    else:
        await message.answer(f"Пользователь {data['id']} имеет {user_sum[0]} рублей на аккаунте", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text='Перевёл', callback_data=f'ipay_{str(user_id)}')]]) 

)
    await state.set_state(AdminState.idle)
    await state.clear()
    await cursor.close()
    await connect.close()

@router.callback_query(lambda c: c.data.startswith('ipay_'))
async def amount_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[1]
    async with aiosqlite.connect("./data/db.db") as connect:
        async with connect.cursor() as cursor:
            await callback.bot.send_message(user_id, f'Средства были успешно отправлены на счет получателя', reply_markup=back_keyboard)
            await cursor.execute('UPDATE users SET sum = 0 WHERE user_id = ?', (user_id,))
            await callback.answer('Отправлено')
            await connect.commit()