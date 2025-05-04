from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from keyboards.keyboard import *
from states.dispatcher import UserState
from handlers.admin import ADMIN_ID
from config.config import CHANNEL_ID
import secrets, aiosqlite



router = Router()
@router.message(F.text == '💵 Продать аккаунт')
async def choose_game(message: types.Message) -> None:
    await message.answer('Выберите игру из списка ниже, по которой хотите продать ваш игровой аккаунт\n<b>ВАЖНО!</b> <i>На одном телеграмм аккаунте не может быть одновременно два и более зарегистрированных объявления</i>', reply_markup=game_keyboard)


def get_game_name(token):
    abbreviation = token[:2].upper()
    game_abbreviations = {
        "BS": "Brawl Stars",
        "CR": "Clash Royale",
        "CC": "Clash of Clans",
        "PM": "Pubg Mobile",
        "ML": "Mobile Legends",
        "RB": "Roblox",
        "ST": "Standoff 2"
    }
    return game_abbreviations.get(abbreviation)

@router.callback_query(lambda c: c.data.startswith(('BS_', 'CR_', 'CC_', 'PM_', 'ML_', 'RB_', 'ST_')))
async def first_step(callback: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    global token
    token_1 = callback.data
    token_2 = secrets.token_urlsafe(8) 
    token = token_1 + token_2
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    await cursor.execute('INSERT into ads (saller_id, token_ad) VALUES (?, ?)', (user_id, token))
    await connect.commit()
    await callback.message.answer(f'<b>Добавьте до трех медиафайлов в заявку(фото или видео). Медиафайлы нужно добавлять поочерёдно!</b>\n\nЭто позволит ей с большим шансом пройти модерацию', reply_markup=back_keyboard)
    await state.set_state(UserState.waiting_for_media_1)
    await cursor.close()
    await connect.close()

async def cont(message: types.Message, state: FSMContext):
    await message.reply("<b>Теперь добавьте описание вашему игровому аккаунту</b>\n\nСделайте его как можно более подробным, и тогда шанс на покупку вашего аккаунта вырастет в разы. ")
    await state.set_state(UserState.waiting_for_description)

@router.message(F.text == '✅ Далее')
async def continue_handler(message: types.Message, state: FSMContext):
    await cont(message, state)

@router.message(UserState.waiting_for_media_1)
async def handle_media(message: types.Message, state: FSMContext):
    global media_ids
    global media_types
    media_ids = []
    media_types = []
    file_id = message.media_group_id if message.media_group_id else message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else message.document.file_id)
    await state.update_data(media_1=file_id)
    if len(media_ids) < 3: 
        media_ids.append(message.media_group_id if message.media_group_id else message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else message.document.file_id))
        media_types.append("photo" if message.photo else ("video" if message.video else None))
        await state.set_state(UserState.waiting_for_media_2)
        await message.reply("<b>Отправьте ещё медиа(не более трёх) или нажмите кнопку Далее, чтобы указать описание игрового аккаунта</b>", reply_markup=con_keyboard)     
    else:   
        await cont(message, state)
    
@router.message(UserState.waiting_for_media_2)
async def handle_media(message: types.Message, state: FSMContext):
    file_id = message.media_group_id if message.media_group_id else message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else message.document.file_id)
    await state.update_data(media_2=file_id)
    if len(media_ids) < 3: 
        media_ids.append(message.media_group_id if message.media_group_id else message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else message.document.file_id))
        media_types.append("photo" if message.photo else ("video" if message.video else None))
        await state.set_state(UserState.waiting_for_media_3)
        await message.reply("<b>Отправьте ещё медиа(не более трёх) или нажмите кнопку Далее, чтобы указать описание игрового аккаунта</b>", reply_markup=con_keyboard)
    else:   
        await cont(message, state)

@router.message(UserState.waiting_for_media_3)
async def handle_media(message: types.Message, state: FSMContext):
    file_id = message.media_group_id if message.media_group_id else message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else message.document.file_id)
    await state.update_data(media_3=file_id)
    if len(media_ids) < 3: 
        media_ids.append(message.media_group_id if message.media_group_id else message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else message.document.file_id))
        media_types.append("photo" if message.photo else ("video" if message.video else None))
        await state.set_state(UserState.waiting_for_media_3)
        await cont(message, state)   

@router.message(UserState.waiting_for_description)
async def handle_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply("<b>Укажите цену для вашего аккаунта</b>\n\nЦена должна соответствовать вашему аккаунту. В противном случае заявка будет отклонена")
    await state.set_state(UserState.waiting_for_price)

@router.message(UserState.waiting_for_price)
async def handle_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(UserState.mail)
    await message.answer('<b>ВНИМАНИЕ!</b>\n\nВаш игровой аккаунт должен быть привязан к электронной почте. Советуем создать новую почту конкретно для этого аккаунта и привязать эту почту. Это сделано для того, чтобы ваш игровой аккаунт был в безопасности\n\n<b>Введите адрес вашей электронной почты</b>')
    
@router.message(UserState.mail)
async def mail_handle(message: types.Message, state: FSMContext):
    await state.update_data(mail=message.text)
    await message.answer('Теперь введите пароль от вашей электронной почты')
    await state.set_state(UserState.password)

@router.message(UserState.password)
async def mail_handle(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(UserState.idle)
    await message.answer('<b>Поздравляем! Вы завершили создание заявки!</b>\n\nНажмите кнопку 🏁 Отправить, чтобы отправить заявку на модерацию администратору или нажмите Вернуться в меню, чтобы очистить форму для заполнения заявки...', reply_markup=fin_keyboard)
    
    
@router.message(F.text == '🏁 Отправить')
async def send_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data() 
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    token_ad = await cursor.execute('SELECT token_ad FROM ads WHERE saller_id = ?', (user_id,))
    token_ad = await token_ad.fetchone()
    game_name = get_game_name(token_ad[0])

    media_items = [] 

    for file_id, media_type in zip(media_ids, media_types):
        if media_type == 'photo':
            media_items.append(InputMediaPhoto(media=file_id))
        if media_type == 'video':
            media_items.append(InputMediaVideo(media=file_id))

    mail = data['mail']
    password = data['password']
    description = data['description']
    cost = int(data['price'])
    percent = round(int(cost * 0.2))
    price = int(percent + cost)

    while len(media_ids) < 3:
        media_ids.append(None)
    while len(media_types) < 3:
        media_types.append(None)

    caption = f"🎮 {game_name} 🎮\n\n💵 Цена: {price}\n\n📄 Описание аккаунта: {description}"
    caption_for_admin = caption + f'\nПочта: {mail}\nПароль: {password}'

    await cursor.execute('UPDATE ads SET about = ?, file_1 = ?, media_type1 = ?, file_2 = ?, media_type2 = ?, file_3 = ?, media_type3 = ?, cost = ?, game_name = ?, mail = ?, password = ?, percentage = ?, full_description = ? WHERE saller_id = ? AND token_ad = ?', (description, media_ids[0], media_types[0], media_ids[1], media_types[1], media_ids[2], media_types[2], price, game_name, mail, password, percent, caption, user_id, token_ad[0]))
    await connect.commit()
    

    await message.bot.send_media_group(ADMIN_ID, media=media_items)
    await message.bot.send_message(ADMIN_ID, caption_for_admin, reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                    [
        [InlineKeyboardButton(text="Принять", callback_data=f"accept_{message.from_user.id}_{token_ad}")],
        [InlineKeyboardButton(text="Отклонить", callback_data=f"decline_{message.from_user.id}_{token_ad}")]
    ]))
    await message.answer(f'<b>Ваша заявка отправлена на модерацию!</b>\n\nОжидайте ответа...', reply_markup=back_keyboard)
    await cursor.close()
    await connect.close()

    

@router.callback_query(lambda c: c.data.startswith('accept_'))
async def process_callback_accept(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[1]
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    token_ad = await cursor.execute('SELECT token_ad FROM ads WHERE saller_id = ?', (user_id,))
    token_ad = await token_ad.fetchone()
    caption = await cursor.execute('SELECT full_description FROM ads WHERE saller_id = ?', (user_id,))
    caption = await caption.fetchone()
    about_ad = await cursor.execute('SELECT file_1, media_type1, file_2, media_type2, file_3, media_type3 FROM ads WHERE saller_id = ?', (user_id,))
    about_ad = await about_ad.fetchone()
    file_1, media_type1, file_2, media_type2, file_3, media_type3, = about_ad

    media_ids = [file_1, file_2, file_3]
    media_types = [media_type1, media_type2, media_type3]
    media_items = []

    for file_id, media_type in zip(media_ids, media_types):
        if media_type == 'photo':
            media_items.append(InputMediaPhoto(media=file_id))
        if media_type == 'video':
            media_items.append(InputMediaVideo(media=file_id))

    url = f'https://t.me/pt_shop_account_bot?start={token_ad[0]}'

    if media_items: 
        media_items[0].caption = f"{caption[0]}\n\n<a href='{url}'>КУПИТЬ АККАУНТ</a>" 
        media_items[0].parse_mode = ParseMode.HTML

        await callback.message.bot.send_media_group(CHANNEL_ID, media=media_items)
       
    await callback.message.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.bot.send_message(int(user_id), "<b>Ваша заявка одобрена!</b>\n\nУ вас есть возможность закрепить свое объявление через нашего администратора", reply_markup=yoo_keyboard)
    await callback.answer('Заявка одобрена')
    await state.clear()
    await cursor.close()
    await connect.close()

@router.callback_query(lambda c: c.data.startswith('decline_'))
async def process_callback_decline(callback: types.CallbackQuery, state: FSMContext):
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    user_id = callback.data.split('_')[1]
    token_ad = await cursor.execute('SELECT token_ad FROM ads WHERE saller_id = ?', (user_id,))
    token_ad = await token_ad.fetchone()
    await cursor.execute('DELETE FROM ads WHERE token_ad = ?', (token_ad[0],))
    await connect.commit()
    await callback.message.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.bot.send_message(int(user_id), "Ваша заявка отклонена")
    await callback.answer('Заявка отклонена')
    await state.clear()
    await cursor.close()
    await connect.close()

    