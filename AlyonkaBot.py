from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from flask import Flask, request
import asyncio, os, random
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------------------
# 🔒 Безопасная загрузка токена
# -----------------------------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в переменные окружения на Koyeb.")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# -----------------------------------------
# 🔥 Firebase
# -----------------------------------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# -----------------------------------------
# 📅 План питания
# -----------------------------------------
plan = {
    "Воскресенье": [
        "завтрак — омлет из одного яйца, сосиска варёная, 40 г гречки + огурчик",
        "обед — рис и красная рыбка в сливках, на десерт яблочко",
        "ужин — салат с курицей, 40 г пасты и сыром",
    ],
    "Понедельник": [
        "завтрак — омлет из одного яйца + 1 белок, варёная сосиска, 40 г овсянки (на воде или овсяном молоке), немного банана",
        "обед — картофельное пюре с куриным филе или индейкой, мягкие тушёные овощи, яблочко",
        "ужин — рисовая лапша с курицей и мягкими овощами, чай ромашковый или мятный",
    ],
}

# -----------------------------------------
# 💬 Комплименты
# -----------------------------------------
compliments = [
    "Ты как свет в конце дня — мягкая и родная.",
    "Когда ты улыбаешься, мир будто перестраивается под твой ритм.",
    "С тобой даже тишина звучит по-другому.",
    "Ты делаешь всё вокруг настоящим.",
    "Ты как утренний свет — тёплая и чистая.",
    "От твоего взгляда становится спокойнее, чем где-либо.",
    "Твоё присутствие лечит лучше любых слов.",
    "Ты заставляешь сердце биться не по правилам.",
    "Ты как дом, в который всегда хочется вернуться.",
    "Ты как музыка, которую невозможно выключить.",
    "От тебя идёт какое-то странное спокойствие и жизнь.",
    "Ты умеешь согревать даже взглядом.",
    "Ты будто создана, чтобы мир был мягче.",
    "Когда ты рядом, всё остальное теряет смысл.",
    "Ты как вдох — естественная и нужная.",
    "С тобой каждый день особенный.",
    "Ты умеешь быть доброй даже в усталости.",
    "Ты как лучик солнца, что пробивается даже сквозь облака.",
    "Ты просто чудо, которое случилось со мной.",
    "Ты делаешь жизнь ярче одним словом.",
    "С тобой всё становится возможным.",
    "Ты моё вдохновение и спокойствие одновременно.",
    "Ты — то, ради чего хочется стать лучше.",
    "Ты особенная. Просто знай это.",
    "Ты как аромат после дождя — свежая и настоящая.",
    "С тобой даже самые простые вещи — радость.",
    "Ты как песня, что живёт в голове и не надоедает.",
    "Ты — уют, который невозможно подделать.",
    "Ты делаешь даже хаос красивым.",
    "Ты моё самое тихое и светлое счастье.",
]

# 💞 Фразы любви
love_phrases = [
    "я тебя тоже безумно люблю!! 💞",
    "а помнишь 12 января, наши первые вебочки? 🥹",
    "всё, что у меня есть — твоё тепло 💗",
    "я счастлив, что именно ТЫ моя 💖",
    "ты — мой дом, моё спокойствие, моё всё 🤍",
    "я бы сейчас обнял тебя так крепко, чтобы ты почувствовала всё 💞",
    "с каждым днём люблю тебя всё сильнее 🌙",
    "ты — причина, почему я улыбаюсь даже ночью 💫",
    "я помню наш первый вечер, каждое слово, каждую улыбку 💭",
    "ты навсегда в моём сердце, Альонка 🤍",
]

# -----------------------------------------
# 🗂 Firebase функции
# -----------------------------------------
def get_status(uid):
    doc = db.collection("users").document(str(uid)).get()
    return doc.to_dict() if doc.exists else {}

def save_status(uid, data):
    db.collection("users").document(str(uid)).set(data)

def get_coupon(uid):
    doc = db.collection("coupons").document(str(uid)).get()
    return doc.to_dict() if doc.exists else {}

def save_coupon(uid, data):
    db.collection("coupons").document(str(uid)).set(data)

# -----------------------------------------
# 🎛 Кнопки
# -----------------------------------------
def bottom_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    kb.add(
        KeyboardButton("Понедельник"), KeyboardButton("Вторник"),
        KeyboardButton("Среда"), KeyboardButton("Четверг"),
        KeyboardButton("Пятница"), KeyboardButton("Суббота"),
        KeyboardButton("Воскресенье"),
    )
    kb.row(KeyboardButton("🎟 Купон на вредность"), KeyboardButton("📊 Статус"))
    kb.add(KeyboardButton("🤍 Я ЛЮБЛЮ ТЕБЯ 🤍"))
    return kb

def meal_kb(day, idx):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Скушала", callback_data=f"done|{day}|{idx}"),
        InlineKeyboardButton("❌ Не кушала", callback_data=f"missed|{day}|{idx}")
    )
    return kb

# -----------------------------------------
# 🚀 Команды
# -----------------------------------------
@dp.message_handler(commands=["start", "меню"])
async def cmd_start(msg: types.Message):
    await msg.answer("Привет, любимая 🤍\nКнопки всегда рядом и удобно!", reply_markup=bottom_menu())

@dp.message_handler(lambda m: m.text == "🤍 Я ЛЮБЛЮ ТЕБЯ 🤍")
async def love_btn(msg: types.Message):
    await msg.answer(random.choice(love_phrases))

# -----------------------------------------
# 🍽 Просмотр плана
# -----------------------------------------
@dp.message_handler(lambda m: m.text and m.text.capitalize() in plan)
async def show_day(msg: types.Message):
    day = msg.text.capitalize()
    meals = plan.get(day, [])
    await msg.answer(f"🍽 План на {day}:", reply_markup=bottom_menu())
    if not meals:
        await msg.answer("Пока шо ничо нема 😇")
        return
    st = get_status(msg.from_user.id)
    for i, meal in enumerate(meals):
        mark = st.get(f"{day}|{meal}", "")
        prefix = "✅" if mark == "✅" else "❌" if mark == "❌" else "•"
        await msg.answer(f"{prefix} {meal}", reply_markup=meal_kb(day, i))

@dp.callback_query_handler(lambda c: c.data.startswith("done"))
async def cb_done(cq: types.CallbackQuery):
    uid = cq.from_user.id
    _, day, idx = cq.data.split("|")
    idx = int(idx)
    meal = plan[day][idx]
    st = get_status(uid)
    st[f"{day}|{meal}"] = "✅"
    save_status(uid, st)
    total_meals = len(plan[day])
    eaten = sum(1 for m in plan[day] if st.get(f"{day}|{m}") == "✅")
    text = f"✅ Молодец, ты съела — {meal}!"
    if eaten == total_meals:
        text += f"\n\n💌 “{random.choice(compliments)}”"
    await cq.message.edit_text(text, reply_markup=meal_kb(day, idx))
    await cq.answer("Отмечено ✅")

@dp.callback_query_handler(lambda c: c.data.startswith("missed"))
async def cb_missed(cq: types.CallbackQuery):
    uid = cq.from_user.id
    _, day, idx = cq.data.split("|")
    idx = int(idx)
    meal = plan[day][idx]
    st = get_status(uid)
    st[f"{day}|{meal}"] = "❌"
    save_status(uid, st)
    await cq.message.edit_text(f"❌ Ты пропустила! Но я всё равно люблю тебя 🤍", reply_markup=meal_kb(day, idx))
    await cq.answer("Отмечено ❌")

# -----------------------------------------
# 📊 Статус
# -----------------------------------------
@dp.message_handler(lambda m: m.text == "📊 Статус")
async def show_status(msg: types.Message):
    uid = msg.from_user.id
    st = get_status(uid)
    if not st:
        await msg.answer("Пока нет отметок 😇", reply_markup=bottom_menu())
        return
    text = "📋 <b>Статус:</b>\n"
    for key, mark in st.items():
        day, meal = key.split("|", 1)
        text += f"{day} — {meal}: {mark}\n"
    await msg.answer(text, parse_mode="HTML", reply_markup=bottom_menu())

# -----------------------------------------
# 🎟 Купон
# -----------------------------------------
@dp.message_handler(lambda m: m.text == "🎟 Купон на вредность")
async def coupon(msg: types.Message):
    uid = msg.from_user.id
    data = get_coupon(uid)
    now = datetime.now()
    if "last" in data:
        last = datetime.fromisoformat(data["last"])
        if now - last < timedelta(days=7):
            await msg.answer("❌ Купон уже активирован (жди 7 дней 😜)", reply_markup=bottom_menu())
            return
    data["last"] = now.isoformat()
    save_coupon(uid, data)
    await msg.answer("🎟 Насладись этой вредностью, моя хорошая 🤍", reply_markup=bottom_menu())

# -----------------------------------------
# 🌐 Flask Webhook сервер
# -----------------------------------------
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    asyncio.run(dp.process_update(types.Update(**update)))
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "✅ Бот работает и слушает Telegram!"

# -----------------------------------------
# ▶️ Запуск (для Koyeb)
# -----------------------------------------
if __name__ == "__main__":
    from threading import Thread
    import time

    async def on_start():
        await bot.delete_webhook()
        await bot.set_webhook("https://superior-rebecca-guyse-55f11288.koyeb.app/webhook")
        print("🚀 Webhook установлен и бот запущен!")

    loop = asyncio.get_event_loop()
    loop.create_task(on_start())

    print("✅ Health-check сервер запущен!")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
