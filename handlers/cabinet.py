from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from keyboards.keyboard import * 
from config.config import YOO_TOKEN, YOO_ACCOUNT
from states.dispatcher import YooState
import html, aiosqlite, uuid, requests, logging, json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
router = Router()

@router.message(F.text == '🏠 Личный кабинет')
async def cabinet(message: types.Message):
    connect = await aiosqlite.connect('./data/db.db')
    cursor = await connect.cursor()
    saller_sum = await cursor.execute('SELECT sum FROM users WHERE user_id = ?', (message.from_user.id,))
    saller_sum = await saller_sum.fetchone()
    await message.answer(f'<b>Добро пожаловать в ваш личный кабинет {html.escape(message.from_user.full_name)}</b>!\n\nСредств на аккаунте: {saller_sum[0]} рублей\n<i>Снять средства можно только через администратора...</i>', reply_markup=yoo_keyboard)
    await cursor.close()
    await connect.close()
        
def make_p2p_transfer(from_account, to_account, amount, comment):
    idempotence_key = str(uuid.uuid4())
    data = {
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "source": { 
            "type": "account",
            "account_number": from_account
        },
        "payee": {
            "type": "account",
            "account_number": to_account
        },
        "comment": comment,
        "message": "Перевод средств",
        "fee_payer": "payee" # Кто платит комиссию
    }

    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {YOO_TOKEN}",
        "Content-Type": "application/json; charset=UTF-8",
        "Idempotence-Key": idempotence_key
    }

    
    logging.info(f"Запрос на перевод: {data}")

    response = requests.post("https://yoomoney.ru/api/request-payment", headers=headers, data=json_data)

    try:
        response_text = response.content.decode('utf-8') # Декодируем ответ
    except UnicodeDecodeError:
        response_text = response.content # Если декодирование не удалось, оставляем как байты
        logging.warning("Не удалось декодировать ответ API. Возможно, ответ содержит бинарные данные.")

    logging.info(f"Ответ API: {response.status_code} {response_text}")

    try:
        response_json = response.json()
    except json.JSONDecodeError:
        logging.error(f"Ошибка декодирования JSON: {response.text}")
        return {"status": "error", "message": "Ошибка обработки ответа от ЮMoney"}

    if response.status_code == 200:
        if "error" in response_json:
            error_code = response_json.get("error")
            error_description = response_json.get("description", "Unknown error")
            logging.error(f"Ошибка ЮMoney: {error_code} - {error_description}")
            return {"status": "error", "message": f"Ошибка ЮMoney: {error_description} (код {error_code})", "code": error_code}
        else:
            operation_id = response_json.get("operation_id")
            logging.info(f"Перевод успешно создан. ID операции: {operation_id}")
            return {"status": "success", "operation_id": operation_id}
    else:
        error_message = response_json.get("description", "Unknown error")
        logging.error(f"Ошибка HTTP: {response.status_code} - {error_message}")
        return {"status": "error", "message": f"HTTP Error: {response.status_code} - {error_message}", "status_code": response.status_code}


@router.callback_query(F.data == 'yoo_pay')
async def yoo_pay_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(YooState.num_account)
    await callback.message.answer('<b>Введите номер счета получателя</b>', reply_markup=back_keyboard)

@router.message(YooState.num_account)
async def yoo_state(message: types.Message, state: FSMContext):
    num_acc = message.text.strip()
    await state.update_data(num_acc=num_acc)
    await state.set_state(YooState.idle) # Убедитесь, что YooState.idle существует
    user_id = message.from_user.id

    async with aiosqlite.connect("./data/db.db") as connect:
        async with connect.cursor() as cursor:
            await cursor.execute('SELECT sum FROM users WHERE user_id = ?', (user_id,))
            saller_sum = await cursor.fetchone()

            if saller_sum:
                amount = "{:.2f}".format(float(saller_sum[0]))
                result = make_p2p_transfer(YOO_ACCOUNT, num_acc, amount, "Перевод средств")

                if result['status'] == "success":
                    await message.answer(f'Средства были успешно отправлены на счет получателя: {num_acc}\nСумма: {saller_sum[0]} рублей', reply_markup=back_keyboard)

                    await cursor.execute('UPDATE users SET sum = 0 WHERE user_id = ?', (user_id,))
                    await connect.commit()
                else:
                    error_message = result.get("message", "Неизвестная ошибка")
                    error_code = result.get("code")
                    await message.answer(f"Ошибка при переводе: {error_message}. Код ошибки: {error_code}. Пожалуйста, обратитесь в поддержку.")
                    print(f"Ошибка создания перевода: {error_message}, code: {error_code}, status_code: {result.get('status_code', 'Unknown')}")


    await state.clear()