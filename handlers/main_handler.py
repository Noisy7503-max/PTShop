from aiogram import types, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards.keyboard import *
from handlers.buy_account import search_ad
import html, aiosqlite

router = Router()

@router.message(CommandStart(deep_link=F.args))
async def args_menu(message: types.Message, command: types.BotCommand = None, ):
    if command and command.args:
        ad_id = command.args
        await search_ad(message, ad_id)
        

@router.message(CommandStart())
async def main_menu(message: types.Message, state: FSMContext = None) -> None: 
    if state: 
        await state.clear()

    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
        
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    check_user = await cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    check_user = await check_user.fetchone()
    if check_user is None:
        await cursor.execute('INSERT INTO users (user_id, full_name, username, sum) VALUES (?, ?, ?, ?)',
                             (user_id, full_name, username, 0))
        await connect.commit()
    await cursor.close()
    await connect.close()
    await message.answer(f'<b>Добро пожаловать в магазин для покупки игровых аккаунтов PTShop {html.escape(message.from_user.full_name)}!</b>\n\nВыберите действие из меню ниже👇', reply_markup=main_keyboard)

@router.message(F.text == '🔙 Вернуться в меню' )
async def back_menu(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await main_menu(message, state)

@router.message(F.text == '🚫 Отменить создание заявки' )
async def back_menu(message: types.Message, state: FSMContext) -> None:
    try:
        user_id = message.from_user.id
        connect = await aiosqlite.connect('./data/db.db')
        cursor = await connect.cursor()
        await cursor.execute('DELETE FROM ads WHERE saller_id = ?', (user_id,))
        await connect.commit()
        await cursor.close()
        await connect.close()
    except Exception as e:
        pass
    await state.clear()
    await main_menu(message, state)

@router.message(F.text == '📄 О нас')
async def about_bot(message: types.Message):
    await message.answer('<b>PTShop - твой надежный помощник в мире игровых аккаунтов!</b>\n\n🚀 У нас вы можете выгодно приобрести или продать аккаунты для таких популярных игр как Brawl Stars, Standoff 2, Mobile Legends и многих других! 🎮 Мечтаешь о топовом аккаунте, но нет времени прокачивать? Или хочешь выгодно продать свой игровой профиль? Мы к твоим услугам! 🛡️ Безопасные сделки, огромный выбор и лучшая цена - гарантированы! Забудь о рисках и мошенниках! Мы обеспечиваем надежность каждой сделки и полную конфиденциальность. Подними свой игровой опыт на новый уровень! Начни работать с нами уже сегодня, и мы обещаем, ты не останешься разочарованным!', reply_markup=canal_keyboard)

@router.message(F.text == '💻 Тех. Поддержка')
async def error_handler(message: types.Message):
    await message.answer('Если у вас возникли вопросы или проблемы или вы знаете как можно улучшить наш магазин, наша служба технической поддержки готова помочь! Мы постараемся ответить вам в кратчайшие сроки... ', reply_markup=yoo_keyboard)




