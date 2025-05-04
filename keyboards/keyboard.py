from aiogram import types


main_kb = [
    [types.KeyboardButton(text='🎮 Купить аккаунт'), types.KeyboardButton(text='💵 Продать аккаунт')],
    [types.KeyboardButton(text='🏠 Личный кабинет')],
    [types.KeyboardButton(text='💻 Тех. Поддержка'), types.KeyboardButton(text='📄 О нас')]
]
main_keyboard = types.ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True)

game_kb = [
    [types.InlineKeyboardButton(text='Brawl Stars', callback_data='BS_')],
    [types.InlineKeyboardButton(text='Clash Royale', callback_data='CR_')],
    [types.InlineKeyboardButton(text='Clash of Clans', callback_data='CC_')],
    [types.InlineKeyboardButton(text='Pubg Mobile', callback_data='PM_')],
    [types.InlineKeyboardButton(text='Mobile Legends', callback_data='ML_')],
    [types.InlineKeyboardButton(text='Roblox', callback_data='RB_')],
    [types.InlineKeyboardButton(text='Standoff 2', callback_data='ST_')]
]
game_keyboard = types.InlineKeyboardMarkup(inline_keyboard=game_kb)

back_kb = [
    [types.KeyboardButton(text='🔙 Вернуться в меню')]
]
back_keyboard = types.ReplyKeyboardMarkup(keyboard=back_kb, resize_keyboard=True)

pay_kb = [
    [types.InlineKeyboardButton(text='💵 Оплатил', callback_data='pay')],
    [types.InlineKeyboardButton(text='Написать администратору', url='https://t.me/')]
]
pay_keyboard = types.InlineKeyboardMarkup(inline_keyboard=pay_kb)

con_kb = [
    [types.KeyboardButton(text='✅ Далее')],
    [types.KeyboardButton(text='🔙 Вернуться в меню')]
]
con_keyboard = types.ReplyKeyboardMarkup(keyboard=con_kb, resize_keyboard=True)

fin_kb = [
    [types.KeyboardButton(text='🏁 Отправить')],
    [types.KeyboardButton(text='🔙 Вернуться в меню')]
]
fin_keyboard = types.ReplyKeyboardMarkup(keyboard=fin_kb, resize_keyboard=True)

finish_kb = [
    [types.KeyboardButton(text='🤝 Завершить сделку')]
]
finish_keyboard = types.ReplyKeyboardMarkup(keyboard=finish_kb, resize_keyboard=True)

finish_da_kb = [
    [types.KeyboardButton(text='🤝 Да, Завершить сделку')]
]
finish_da_keyboard = types.ReplyKeyboardMarkup(keyboard=finish_da_kb, resize_keyboard=True)

yoo_kb = [
    #[types.InlineKeyboardButton(text='Перевести на счёт Yoo Money', callback_data='yoo_pay')],
    [types.InlineKeyboardButton(text='Написать администратору', url='https://t.me/aleksptshop')]
]
yoo_keyboard = types.InlineKeyboardMarkup(inline_keyboard=yoo_kb)

canal_kb = [
    #[types.InlineKeyboardButton(text='Перевести на счёт Yoo Money', callback_data='yoo_pay')],
    [types.InlineKeyboardButton(text='📢 Подписатья на канал', url='https://t.me/ptshopgames')]
]
canal_keyboard = types.InlineKeyboardMarkup(inline_keyboard=canal_kb)

cancel_kb = [
    [types.KeyboardButton(text='🚫 Отменить создание заявки')]
]
cancel_keyboard = types.ReplyKeyboardMarkup(keyboard=cancel_kb, resize_keyboard=True)

admin_kb = [
    [types.InlineKeyboardButton(text='Рассылка', callback_data='send')], 
    [types.InlineKeyboardButton(text='Статистика', callback_data='amount_user')],
    [types.InlineKeyboardButton(text='Счет пользователя', callback_data='amount_rub')]
]
admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_kb)

ipay_kb = [
    [types.InlineKeyboardButton(text='Перевёл', callback_data='ipay')]
]
ipay_keyboard = types.InlineKeyboardMarkup(inline_keyboard=ipay_kb)