import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from openai import AsyncOpenAI

import os
BOT_TOKEN = os.environ["BOT_TOKEN"]
PROXYAPI_KEY = os.environ["PROXYAPI_KEY"]

PRICE_ONE_CARD = 50
PRICE_THREE_CARDS = 120

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = AsyncOpenAI(
    base_url="https://api.proxyapi.ru/openai/v1",
    api_key=PROXYAPI_KEY,
)

MAJOR_ARCANA = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюблённые", "Колесница", "Сила", "Отшельник",
    "Колесо Фортуны", "Справедливость", "Повешенный", "Смерть",
    "Умеренность", "Дьявол", "Башня", "Звезда", "Луна", "Солнце",
    "Суд", "Мир"
]

MINOR_ARCANA = [
    "Туз Жезлов", "Двойка Жезлов", "Тройка Жезлов", "Четвёрка Жезлов",
    "Туз Кубков", "Двойка Кубков", "Тройка Кубков", "Четвёрка Кубков",
    "Туз Мечей", "Двойка Мечей", "Тройка Мечей", "Четвёрка Мечей",
    "Туз Пентаклей", "Двойка Пентаклей", "Тройка Пентаклей", "Четвёрка Пентаклей"
]

FULL_DECK = MAJOR_ARCANA + MINOR_ARCANA

user_state = {}
user_name = {}
user_gender = {}
user_birthdate = {}
user_question = {}
user_paid = {}

MALE_NAMES = {
    "александр", "саша", "шура", "саня", "алексей", "алёша", "лёша", "андрей", "андрюша",
    "антон", "антоша", "артём", "артемий", "тёма", "борис", "боря", "вадим", "вадик",
    "валентин", "валя", "валерий", "валера", "василий", "вася", "виктор", "витя",
    "виталий", "виталик", "владимир", "вова", "володя", "владислав", "влад",
    "вячеслав", "слава", "геннадий", "гена", "георгий", "гоша", "григорий", "гриша",
    "даниил", "данила", "даня", "денис", "ден", "дмитрий", "дима", "димон",
    "евгений", "женя", "егор", "иван", "ваня", "игорь", "илья", "илюша",
    "кирилл", "киря", "константин", "костя", "лев", "лёва", "леонид", "лёня",
    "максим", "макс", "марк", "матвей", "михаил", "миша", "никита",
    "николай", "олег", "павел", "паша", "пётр", "петя", "роман", "рома",
    "руслан", "сергей", "серёжа", "станислав", "стас", "степан", "стёпа",
    "тимофей", "тимоха", "фёдор", "федя", "эдуард", "эдик", "юрий", "юра",
    "яков", "яша", "ярослав", "ярик", "артур", "арсен", "рустам", "тимур",
    "булат", "дамир", "карим", "марат", "ренат", "эмиль", "альберт", "богдан",
    "давид", "демьян", "ефим", "захар", "игнат", "климент", "лука", "мстислав",
    "назар", "платон", "савелий", "семён", "тарас", "трофим", "харитон",
    "эрик", "ян", "ждан", "радим", "ратибор", "святогор", "яромир"
}

FEMALE_NAMES = {
    "александра", "саша", "шура", "александрина", "алина", "аля", "алёна",
    "алена", "алиса", "алла", "альбина", "анастасия", "настя", "ангелина",
    "анжела", "анжелика", "анна", "аня", "антонина", "тоня", "арина",
    "валентина", "валя", "валерия", "лера", "варвара", "варя", "вера",
    "вероника", "вика", "виктория", "виолетта", "вита", "галина", "галя",
    "дарья", "даша", "диана", "дина", "ева", "евгения", "женя", "екатерина",
    "катя", "елена", "лена", "елизавета", "лиза", "жанна", "зинаида", "зина",
    "зоя", "инга", "инесса", "инна", "ирина", "ира", "карина", "каролина",
    "кира", "клавдия", "клава", "кристина", "кристи", "ксения", "ксюша",
    "лариса", "лара", "лидия", "лида", "лилия", "лиля", "любовь", "люба",
    "людмила", "люда", "маргарита", "рита", "марина", "мариша", "мария",
    "маша", "марфа", "надежда", "надя", "наталья", "наташа", "нелли",
    "нина", "оксана", "ольга", "оля", "полина", "прасковья", "раиса",
    "регина", "светлана", "света", "софия", "соня", "софья", "таисия",
    "таисия", "тамара", "тома", "татьяна", "таня", "ульяна", "уля",
    "эльвира", "эля", "юлия", "юля", "яна", "янина", "милана", "милена",
    "эвелина", "эмма", "стелла", "роза", "лиана", "лада", "злата"
}

def detect_gender(name):
    name_lower = name.lower().strip()
    if name_lower in MALE_NAMES:
        return "male"
    elif name_lower in FEMALE_NAMES:
        return "female"
    else:
        return "unknown"

def get_pronouns(gender):
    if gender == "male":
        return {
            "dear": "дорогой",
            "came": "пришёл",
            "welcome": "рад",
            "client": "клиент",
            "clientka": "клиента",
        }
    else:
        return {
            "dear": "дорогая",
            "came": "пришла",
            "welcome": "рада",
            "client": "клиентка",
            "clientka": "клиентки",
        }

def get_zodiac_sign(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Овен", "огонь"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Телец", "земля"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Близнецы", "воздух"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Рак", "вода"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Лев", "огонь"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Дева", "земля"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Весы", "воздух"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Скорпион", "вода"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Стрелец", "огонь"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Козерог", "земля"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Водолей", "воздух"
    else:
        return "Рыбы", "вода"

def calculate_age(birthdate):
    today = datetime.now()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def generate_reading(name, gender, birthdate, question, cards_list):
    age = calculate_age(birthdate)
    zodiac, element = get_zodiac_sign(birthdate.day, birthdate.month)
    p = get_pronouns(gender)

    cards_text = ""
    if len(cards_list) == 1:
        cards_text = f"ВЫПАВШАЯ КАРТА: {cards_list[0]}."
    elif len(cards_list) == 3:
        cards_text = f"ВЫПАВШИЕ КАРТЫ:\n- Прошлое: {cards_list[0]}\n- Настоящее: {cards_list[1]}\n- Будущее: {cards_list[2]}"
    else:
        cards_text = f"ВЫПАВШИЕ КАРТЫ: {', '.join(cards_list)}."

    prompt = (
        f"Ты — опытный таролог, практикующий более 20 лет. К тебе пришёл {p['client']}.\n\n"
        f"ДАННЫЕ {p['client'].upper()}А:\n"
        f"- Имя: {name}\n"
        f"- Дата рождения: {birthdate.strftime('%d.%m.%Y')} (возраст: {age} лет)\n"
        f"- Знак зодиака: {zodiac}\n"
        f"- Стихия: {element}\n"
        f"- Ситуация или вопрос: {question}\n\n"
        f"{cards_text}\n\n"
        f"ВАЖНО: обращайся к {p['client']}у в {'мужском' if gender == 'male' else 'женском'} роде.\n"
        f"Используй обращения «{name}», «{p['dear']} {name}», «{p['dear']}».\n\n"
        f"ТВОЯ ЗАДАЧА:\n"
        f"1. Начни ответ с обращения по имени.\n"
        f"2. Объясни значение выпавших карт — конкретно, не общими фразами.\n"
        f"3. Если карт несколько, объясни их взаимосвязь.\n"
        f"4. Свяжи карты со знаком зодиака {zodiac} и стихией {element}.\n"
        f"5. Учитывай возраст ({age} лет) — дай совет для этого этапа.\n"
        f"6. Обратись напрямую к ситуации/вопросу.\n"
        f"7. Заверши личным советом и предсказанием на месяц.\n\n"
        f"СТИЛЬ ОТВЕТА:\n"
        f"- Говори заботливо, но без лести. Как мудрый таролог.\n"
        f"- Используй {'мужской' if gender == 'male' else 'женский'} род (пришёл, сделал, подумал, готов).\n"
        f"- Ответ — 8-10 предложений, 2-3 абзаца."
    )

    return prompt

@dp.message(Command("start"))
async def start(message: types.Message):
    welcome = (
        "✨ *Добро пожаловать в Ателье Судьбы* ✨\n\n"
        "Я твой личный таролог. Карты не врут, они лишь говорят то, что ты боишься услышать.\n\n"
        "🌙 *Один расклад — одна судьба.*\n"
        "Первый расклад для тебя — бесплатно.\n\n"
        "⚜️ *Команды:*\n"
        "/one — бесплатный расклад (один раз)\n"
        "/buy — купить платный расклад\n"
        "/about — обо мне"
    )
    await message.answer(welcome, parse_mode="Markdown")

@dp.message(Command("about"))
async def about(message: types.Message):
    await message.answer(
        "🃏 *Ателье Судьбы* — это твой личный оракул.\n\n"
        "Я использую древнюю мудрость Таро и современные технологии, "
        "чтобы дать тебе самый точный и глубокий расклад.\n\n"
        "Каждая карта — это ключ к твоему подсознанию. "
        "Доверься мне, и я покажу то, что скрыто от глаз.",
        parse_mode="Markdown"
    )

@dp.message(Command("one"))
async def one_card_start(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_paid:
        await message.answer(
            "🌙 Ты уже получил свой бесплатный расклад.\n\n"
            "Используй /buy чтобы получить ещё более глубокие расклады."
        )
        return

    user_state[user_id] = "waiting_name_free"
    await message.answer("🌙 Для начала скажи, как тебя зовут?")

@dp.message(Command("buy"))
async def buy(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=f"🃏 1 карта ({PRICE_ONE_CARD} ⭐)", callback_data="pay_one")],
        [types.InlineKeyboardButton(text=f"🔮 3 карты ({PRICE_THREE_CARDS} ⭐)", callback_data="pay_three")]
    ])
    await message.answer(
        "💎 *Выбери глубину расклада:*\n\n"
        f"🃏 *1 карта* — {PRICE_ONE_CARD} ⭐\n"
        f"🔮 *3 карты* — прошлое, настоящее, будущее — {PRICE_THREE_CARDS} ⭐\n\n"
        "Оплата через Telegram Stars.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.in_(["pay_one", "pay_three"]))
async def process_payment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    payment_type = callback.data
    
    if payment_type == "pay_one":
        title = "Расклад на 1 карту"
        description = "Глубокий персонализированный расклад с толкованием"
        price = PRICE_ONE_CARD
        payload = f"paid_one_{user_id}"
    else:
        title = "Расклад на 3 карты"
        description = "Прошлое, настоящее и будущее — полная картина твоей судьбы"
        price = PRICE_THREE_CARDS
        payload = f"paid_three_{user_id}"
    
    await bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label=title, amount=price)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    
    if payload.startswith("paid_one_"):
        user_paid[user_id] = "one"
        user_state[user_id] = "waiting_name_paid"
        await message.answer("💫 Отлично! Сейчас начнём твой платный расклад.\n\nДля начала скажи, как тебя зовут?")
    
    elif payload.startswith("paid_three_"):
        user_paid[user_id] = "three"
        user_state[user_id] = "waiting_name_paid"
        await message.answer("💫 Отлично! Сейчас начнём твой платный расклад.\n\nДля начала скажи, как тебя зовут?")

@dp.message(F.text)
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if state == "waiting_name_free":
        name = message.text.strip()
        user_name[user_id] = name
        detected_gender = detect_gender(name)
        if detected_gender == "unknown":
            user_state[user_id] = "waiting_gender_free"
            await message.answer(f"🌸 *{name}*, я хочу обращаться к тебе правильно.\nТы парень или девушка? Напиши «парень» или «девушка».", parse_mode="Markdown")
        else:
            user_gender[user_id] = detected_gender
            p = get_pronouns(detected_gender)
            user_state[user_id] = "waiting_birthdate_free"
            await message.answer(f"💫 *{name}*, {p['dear']} мой, я чувствую твою энергию...\nНазови свою дату рождения в формате ДД.ММ.ГГГГ (например, 15.06.1998).\nЭто ключ к твоей судьбе.", parse_mode="Markdown")

    elif state == "waiting_gender_free":
        answer = message.text.lower().strip()
        if answer in ["парень", "м", "мужчина", "мужской", "мужик"]:
            user_gender[user_id] = "male"
        elif answer in ["девушка", "ж", "женщина", "женский", "девочка"]:
            user_gender[user_id] = "female"
        else:
            await message.answer("🌸 Напиши просто «парень» или «девушка».")
            return
        p = get_pronouns(user_gender[user_id])
        name = user_name.get(user_id, "")
        user_state[user_id] = "waiting_birthdate_free"
        await message.answer(f"💫 *{name}*, {p['dear']} мой, теперь я знаю как к тебе обращаться.\nНазови свою дату рождения в формате ДД.ММ.ГГГГ (например, 15.06.1998).\nЭто ключ к твоей судьбе.", parse_mode="Markdown")

    elif state == "waiting_birthdate_free":
        try:
            birthdate = datetime.strptime(message.text, "%d.%m.%Y")
            user_birthdate[user_id] = birthdate
            user_state[user_id] = "waiting_question_free"
            await message.answer("✨ Теперь звёзды видят тебя...\n\nРасскажи мне свою ситуацию или задай вопрос.\nНе бойся, говори открыто — всё останется между нами.")
        except ValueError:
            await message.answer("🌸 Пожалуйста, введи дату в формате ДД.ММ.ГГГГ (например, 15.06.1998).")
            return

    elif state == "waiting_question_free":
        user_question[user_id] = message.text
        user_paid[user_id] = "used_free"
        await message.answer("🃏 Я взываю к древним силам... Карты шепчут твоё имя...")
        
        name = user_name.get(user_id, "Гость")
        gender = user_gender.get(user_id, "female")
        birthdate = user_birthdate.get(user_id)
        question = user_question.get(user_id)
        card = random.choice(FULL_DECK)
        
        prompt = generate_reading(name, gender, birthdate, question, [card])
        try:
            completion = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.95,
                max_tokens=600
            )
            result = completion.choices[0].message.content
            final_message = (
                f"🃏 *Твоя карта:* {card}\n\n"
                f"{result}\n\n"
                f"🌙 Понравился расклад? Используй /buy чтобы получить ещё более глубокий."
            )
            await message.answer(final_message, parse_mode="Markdown")
        except Exception as e:
            await message.answer("⚠️ Карты сегодня утомлены. Попробуй позже.")
        user_state[user_id] = None

    elif state == "waiting_name_paid":
        name = message.text.strip()
        user_name[user_id] = name
        detected_gender = detect_gender(name)
        if detected_gender == "unknown":
            user_state[user_id] = "waiting_gender_paid"
            await message.answer(f"🌸 *{name}*, я хочу обращаться к тебе правильно.\nТы парень или девушка? Напиши «парень» или «девушка».", parse_mode="Markdown")
        else:
            user_gender[user_id] = detected_gender
            p = get_pronouns(detected_gender)
            user_state[user_id] = "waiting_birthdate_paid"
            await message.answer(f"💫 *{name}*, {p['dear']} мой, я чувствую твою энергию...\nНазови свою дату рождения в формате ДД.ММ.ГГГГ (например, 15.06.1998).\nЭто ключ к твоей судьбе.", parse_mode="Markdown")

    elif state == "waiting_gender_paid":
        answer = message.text.lower().strip()
        if answer in ["парень", "м", "мужчина", "мужской", "мужик"]:
            user_gender[user_id] = "male"
        elif answer in ["девушка", "ж", "женщина", "женский", "девочка"]:
            user_gender[user_id] = "female"
        else:
            await message.answer("🌸 Напиши просто «парень» или «девушка».")
            return
        p = get_pronouns(user_gender[user_id])
        name = user_name.get(user_id, "")
        user_state[user_id] = "waiting_birthdate_paid"
        await message.answer(f"💫 *{name}*, {p['dear']} мой, теперь я знаю как к тебе обращаться.\nНазови свою дату рождения в формате ДД.ММ.ГГГГ (например, 15.06.1998).\nЭто ключ к твоей судьбе.", parse_mode="Markdown")

    elif state == "waiting_birthdate_paid":
        try:
            birthdate = datetime.strptime(message.text, "%d.%m.%Y")
            user_birthdate[user_id] = birthdate
            user_state[user_id] = "waiting_question_paid"
            await message.answer("✨ Теперь звёзды видят тебя...\n\nРасскажи мне свою ситуацию или задай вопрос.\nНе бойся, говори открыто — всё останется между нами.")
        except ValueError:
            await message.answer("🌸 Пожалуйста, введи дату в формате ДД.ММ.ГГГГ (например, 15.06.1998).")
            return

    elif state == "waiting_question_paid":
        user_question[user_id] = message.text
        await message.answer("🃏 Я взываю к древним силам... Карты шепчут твоё имя...")
        
        name = user_name.get(user_id, "Гость")
        gender = user_gender.get(user_id, "female")
        birthdate = user_birthdate.get(user_id)
        question = user_question.get(user_id)

        paid_type = user_paid.get(user_id, "one")

        if paid_type == "one":
            cards_list = [random.choice(FULL_DECK)]
        elif paid_type == "three":
            cards_list = [random.choice(FULL_DECK) for _ in range(3)]
        else:
            cards_list = [random.choice(FULL_DECK)]
        
        prompt = generate_reading(name, gender, birthdate, question, cards_list)
        try:
            completion = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.95,
                max_tokens=800
            )
            result = completion.choices[0].message.content
            
            if paid_type == "one":
                final_message = (
                    f"🃏 *Твоя карта:* {cards_list[0]}\n\n"
                    f"{result}\n\n"
                    f"🌙 Благодарю за доверие! Возвращайся за новыми раскладами."
                )
            elif paid_type == "three":
                final_message = (
                    f"🔮 *Твой расклад на 3 карты:*\n"
                    f"🌑 Прошлое: {cards_list[0]}\n"
                    f"🌓 Настоящее: {cards_list[1]}\n"
                    f"🌕 Будущее: {cards_list[2]}\n\n"
                    f"{result}\n\n"
                    f"🌙 Благодарю за доверие! Возвращайся за новыми раскладами."
                )
            await message.answer(final_message, parse_mode="Markdown")
        except Exception as e:
            await message.answer("⚠️ Карты сегодня утомлены. Попробуй позже.")
        user_state[user_id] = None

asyncio.run(dp.start_polling(bot))