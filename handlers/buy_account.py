from aiogram import types, F, Router
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from yoomoney import Quickpay
from keyboards.keyboard import *
from states.dispatcher import client
from datetime import timedelta
import aiosqlite, uuid, asyncio

router = Router()
tasks = {}

@router.message(F.text == '🎮 Купить аккаунт')
async def buy_handler(message: types.Message) -> None:
    await message.answer('<b>Чтобы купить аккаунт перейдите в наш канал с объявлениями и выберите любой понравившийся пост</b>', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📢 Подписаться на канал', url='https://t.me/ptshopgames')]]))


async def search_ad(message: types.Message, ad_token):
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    global token_ad
    token_ad = ad_token
    about_ad = await cursor.execute('SELECT about, file_1, media_type1, file_2, media_type2, file_3, media_type3, cost, game_name, mail, password FROM ads WHERE token_ad = ?', (ad_token,))
    about_ad = await about_ad.fetchone()
    if about_ad == None:
        await message.answer('К сожалению этот аккаунт больше не в продаже :( ')
    else:
        global mail
        global password
        about, file_1, media_type1, file_2, media_type2, file_3, media_type3, cost, game_name, mail, password = about_ad
        media_ids = [file_1, file_2, file_3]
        media_types = [media_type1, media_type2, media_type3]
        media_items = []

        for file_id, media_type in zip(media_ids, media_types):
            if media_type == 'photo':
                media_items.append(InputMediaPhoto(media=file_id))
            if media_type == 'video':
                media_items.append(InputMediaVideo(media=file_id))

        caption = f"🎮 {game_name} 🎮\n\n💵 Цена: {cost}\n\n📄 Описание аккаунта: {about}"

        if media_items: 
            media_items[0].caption = caption 
            media_items[0].parse_mode = ParseMode.HTML
        
        global label
        label = str(uuid.uuid4())

        quickpay = Quickpay(
                receiver="4100118970052190", # Номер вашего аккаунта
                quickpay_form="shop", # Это я хз зачем, но я это не трогаю
                targets="Pay an account", # Цели, я их не изменяю, потому что особой нужды в этом нет.
                paymentType="SB", # Это лучше не трогать
                sum=cost, # Это сумма
                label=label # Это комментарий для проверки на наличие оплаты
                )
        pay_url = quickpay.base_url

        await message.bot.send_media_group(message.from_user.id, media=media_items)
        await message.answer(f'<b>Чтобы купить данный аккаунт, вы должны внести оплату в нашего бота</b>\n\n<a href="{pay_url}">ССЫЛКА ДЛЯ ОПЛАТЫ</a>\n\nВНИМАНИЕ!\n<i>После внесения оплаты нажмите</i> <b>Оплатил</b> <i>вам будет выданы почта, на которую придёт код подтверждения и пароль от этой почты. Далее вы сможете приступить к проверке аккаунта, после которой вам нужно Завершить сделку. Если в течение 48 часов после получения почты и пароля вы не завершите сделку, бот сделает это за вас. В течение этого времени у вас есть возможность сделать возврат средств через нашего администратора...</i>', reply_markup=pay_keyboard, parse_mode='HTML', disable_web_page_preview=True)
        await cursor.close()
        await connect.close()

@router.callback_query(F.data == 'pay')
async def pay_handler(callback: types.CallbackQuery):
    history = client.operation_history(label=label) 

    if history.operations == []:
        await callback.answer("Оплата не найдена!")

    for operation in history.operations:
        if operation.status == 'success':
            await callback.answer("Оплата найдена!")
            user_id = callback.from_user.id
            ad_id = token_ad
            connect = await aiosqlite.connect('./data/db.db')
            cursor = await connect.cursor()
            about_ad = await cursor.execute('SELECT saller_id, about, file_1, media_type1, file_2, media_type2, file_3, media_type3, cost, game_name, mail, password, percentage FROM ads WHERE token_ad = ?', (token_ad,))
            about_ad = await about_ad.fetchone()
            saller_id, about, file_1, media_type1, file_2, media_type2, file_3, media_type3, cost, game_name, mail, password, percentage = about_ad
            media_ids = [file_1, file_2, file_3]
            media_types = [media_type1, media_type2, media_type3]
            await cursor.execute('DELETE FROM ads WHERE ad_token = ?', (token_ad,))
            await connect.commit()
            await cursor.execute('INSERT into in_sall (saller_id, token_ad, about, file_1, media_type1, file_2, media_type2, file_3, media_type3, cost, game_name, mail, password, percentage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (saller_id, token_ad, about, media_ids[0], media_types[0], media_ids[1], media_types[1], media_ids[2], media_types[2], cost, game_name, mail, password, percentage))
            await connect.commit()
            await callback.message.answer(f'<b>Данные для входа в аккаунт</b>\n\nПочта: {mail}\nПароль от почты: {password}\n\n<i>Чтобы войти в аккаунт, сперва войдите в почту</i>', reply_markup=finish_keyboard)
            await cursor.close()
            await connect.close()
            await schedule_auto_completion(callback.message, user_id, ad_id)


@router.message(F.text == '🤝 Завершить сделку')
async def finish_handler(message: types.Message):
    await message.answer('<b>Вы точно хотите Завершить сделку?</b>\n\nПосле завершения сделки плата за аккаунт перейдет продавцу. Вы больше не сможете сделать возврат средств', reply_markup=finish_da_keyboard)

@router.message(F.text == '🤝 Да, Завершить сделку')
async def finish_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in tasks:
        ad_id = tasks[user_id].get("ad_id")
        tasks[user_id]["event"].set() 

        try:
            tasks[user_id]["task"].cancel()
            await tasks[user_id]["task"] 
        except asyncio.CancelledError:
            pass 

        del tasks[user_id]
        if ad_id:
            await complete_transaction(message, ad_id)
            

async def schedule_auto_completion(message, user_id, ad_id):
    event = asyncio.Event()
    task = asyncio.create_task(delayed_execution(message, event, user_id, ad_id))
    tasks[user_id] = {"task": task, "event": event, "ad_id": ad_id}


async def delayed_execution(message: types.Message, event, user_id, ad_id):
    try:
        await asyncio.sleep(timedelta(hours=48).total_seconds())
        if not event.is_set(): 
            await complete_transaction(message, ad_id)
    except asyncio.CancelledError:
        pass 

async def complete_transaction(message, ad_id):
    try:
        async with aiosqlite.connect("./data/db.db") as connect:
            async with connect.cursor() as cursor:

                await cursor.execute('SELECT saller_id, token_ad FROM ads WHERE token_ad = ?', (ad_id,))
                result = await cursor.fetchone()

                if result:
                    saller_id, token_ad = result
                    full_name = message.from_user.full_name
                    username = message.from_user.username
                    user_id = message.from_user.id
                    url_user = f'https://t.me/{username}'

                    await message.bot.send_message(user_id, f'Сделка состоялась! Спасибо вам за покупку!')
                    await message.bot.send_message(saller_id, f'<b>Сделка состоялась!\nВаш покупатель: <a href="{url_user}">{full_name}</a></b>\n\nСредства будут зачислены на ваш счет в личном кабинете...', reply_markup=back_keyboard, disable_web_page_preview=True)

                    await cursor.execute('SELECT sum FROM users WHERE user_id = ?', (saller_id,))
                    saller_sum = await cursor.fetchone()

                    await cursor.execute('SELECT percentage, cost FROM ads WHERE token_ad = ?', (token_ad,))
                    summa = await cursor.fetchone()
                    percent, cost = summa

                    check = int(cost) - int(percent)
                    saller_sum = int(saller_sum[0]) + check

                    await cursor.execute('UPDATE users SET sum = ? WHERE user_id = ?', (saller_sum, saller_id))
                    await connect.commit()


    except Exception as e:
        print(f"Ошибка при завершении транзакции: {e}")




  

