from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.executor import start_webhook
from datetime import datetime, timedelta
import os, json, random
import firebase_admin
from firebase_admin import credentials, firestore
from aiohttp import web

# -----------------------------------------
# 🔐 Безопасная загрузка токена и Firebase
# -----------------------------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в переменные окружения на Koyeb.")

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# -----------------------------------------
# 🗂 Работа с Firestore
# -----------------------------------------
def get_user_doc(uid):
    return db.collection("users").document(str(uid))

def get_status(uid):
    doc = get_user_doc(uid).get()
    return doc.to_dict().get("status", {}) if doc.exists else {}

def save_status(uid, data):
    get_user_doc(uid).set({"status": data}, merge=True)

def get_coupon(uid):
    doc = get_user_doc(uid).get()
    return doc.to_dict().get("coupon", {}) if doc.exists else {}

def save_coupon(uid, data):
    get_user_doc(uid).set({"coupon": data}, merge=True)

# -----------------------------------------
# 📅 План питания
# -----------------------------------------
if os.path.exists("plan.json"):
    with open("plan.json", "r", encoding="utf-8") as f:
        plan = json.load(f)
else:
    plan = {
        "Понедельник": [
            "завтрак — омлет с сосиской и гречкой",
            "обед — картофельное пюре с курицей",
            "ужин — рисовая лапша с овощами",
        ]
    }

# -----------------------------------------
# 💬 Комплименты
# -----------------------------------------
compliments = [
    "Когда ты рядом, шо-то внутри просто стирается и начинается заново.",
    "Ты не просто красивая, ты как буря, шо может и спалить, и согреть.",
    "От тебя идёт такая энергия, шо даже стены будто начинают слушать.",
    "В тебе столько жизни, шо мир вокруг выглядит серым, если тебя нет.",
    "Шо ты со мной делаешь вообще, я ж просто хотел спокойно существовать.",
    "Ты как запах детства, шо вдруг появился, и сердце сразу зажало.",
    "Когда ты смотришь, я забываю, шо хотел сказать, просто ловлю момент.",
    "Ты такая настоящая, шо даже боль рядом с тобой кажется живой.",
    "В твоей тишине больше смысла, чем в чужих криках.",
    "Мне не нужен идеальный мир, если в нём нет тебя, шо мне с ним тогда.",
    "Иногда ты просто говоришь слово, а у меня всё внутри будто сжимается.",
    "Ты не та, кого можно забыть, ты та, шо остается даже в снах.",
    "Тебя нельзя описать словами, шо бы я ни сказал — всё будет меньше, чем ты.",
    "Ты умеешь смотреть так, шо даже совесть замирает.",
    "Шо бы я ни делал, мысли всё равно возвращаются к тебе.",
    "Ты как огонь, шо не светит, а греет до костей.",
    "Когда ты улыбаешься, время будто останавливается, чтоб просто не мешать.",
    "В тебе есть какая-то странная сила, шо делает меня спокойнее и беспомощнее одновременно.",
    "Твоя хрупкость — это не слабость, а напоминание, шо живое тоже может быть сильным.",
    "Когда ты просто молчишь, у меня ощущение, шо я слышу всё, шо не сказано.",
    "Ты редкая, шо-то вроде случайного чуда, которое не повторяется.",
    "После тебя не пусто, после тебя тихо и светло.",
    "Ты умеешь быть собой даже в хаосе, и это сносит голову.",
    "Когда ты дышишь рядом, сердце делает вид, шо ему всё равно, но оно дрожит.",
    "Если бы чувства имели цвет, ты была бы всеми сразу, шо только можно представить.",
    "Тебя не хочется просто видеть, тебя хочется чувствовать.",
    "Когда я думаю о тебе, всё внутри становится теплее, шо бы ни происходило.",
    "Ты не просто в моей жизни, ты в ней выросла, как часть меня.",
    "Ты такая, шо до конца понять невозможно, и в этом весь кайф.",
    "Даже если бы я умел идеально подбирать слова, всё равно не смог бы сказать, шо чувствую рядом с тобой.",
]

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
    kb.row(
        KeyboardButton("🎟 Купон на вредность"),
        KeyboardButton("📊 Статус"),
    )
    kb.add(KeyboardButton("🤍 Я ЛЮБЛЮ ТЕБЯ 🤍"))
    return kb

def meal_kb(day: str, idx: int):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Скушала", callback_data=f"done|{day}|{idx}"),
        InlineKeyboardButton("❌ Не кушала", callback_data=f"missed|{day}|{idx}"),
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
# 🍽 План питания
# -----------------------------------------
@dp.message_handler(lambda m: m.text and m.text.capitalize() in plan)
async def show_day(msg: types.Message):
    day = msg.text.capitalize()
    meals = plan.get(day, [])
    if not meals:
        await msg.answer(f"На {day} пока нет блюд 😇", reply_markup=bottom_menu())
        return

    st = get_status(msg.from_user.id)
    await msg.answer(f"🍽 План на {day}:")
    for i, meal in enumerate(meals):
        mark = st.get(f"{day}|{meal}", "")
        prefix = "✅" if mark == "✅" else "❌" if mark == "❌" else "•"
        await msg.answer(f"{prefix} {meal}", reply_markup=meal_kb(day, i))

# ✅ / ❌ отметки
@dp.callback_query_handler(lambda c: c.data.startswith(("done", "missed")))
async def cb_meal(cq: types.CallbackQuery):
    uid = cq.from_user.id
    action, day, idx = cq.data.split("|")
    idx = int(idx)
    meal = plan[day][idx]

    st = get_status(uid)
    st[f"{day}|{meal}"] = "✅" if action == "done" else "❌"
    save_status(uid, st)

    if action == "done":
        await cq.message.edit_text(f"✅ Молодец, ты съела — {meal}!\n\n{random.choice(compliments)}",
                                   reply_markup=meal_kb(day, idx))
    else:
        await cq.message.edit_text(f"❌ Ты пропустила... Но я всё равно дуже люблю тебя 🤍",
                                   reply_markup=meal_kb(day, idx))

    # Если день полностью выполнен — комплимент
    meals_today = [f"{day}|{m}" for m in plan[day]]
    marks = [st.get(m, "") for m in meals_today]
    if all(m == "✅" for m in marks if m):
        await bot.send_message(uid, f"🌸 А вот твой заветный комплимент за то, что ты придерживалась дня:\n\n«{random.choice(compliments)}»")

    await cq.answer("Отмечено!")

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
# 🎟 Купон на вредность
# -----------------------------------------
@dp.message_handler(lambda m: m.text == "🎟 Купон на вредность")
async def coupon(msg: types.Message):
    uid = msg.from_user.id
    data = get_coupon(uid)
    now = datetime.now()
    if "last" in data:
        last = datetime.fromisoformat(data["last"])
        if now - last < timedelta(days=7):
            await msg.answer("❌ Купон уже активирован (йолки палки, надо ждать 7 дн 😅)", reply_markup=bottom_menu())
            return
    data["last"] = now.isoformat()
    save_coupon(uid, data)
    await msg.answer("🎟 Насладись этим купоном! 🍫\nТы заслужила 🤍", reply_markup=bottom_menu())

# -----------------------------------------
# 🌐 Webhook + Health-check
# -----------------------------------------
WEBHOOK_HOST = "https://superior-rebecca-guyse-55f11288.koyeb.app/"  # ⚠️ замени на свой домен из Koyeb!
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8080))

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    print("🚀 Webhook установлен и бот запущен!")

async def on_shutdown(dp):
    await bot.delete_webhook()
    print("🛑 Webhook удалён.")

# Health-check для Koyeb
async def health(request):
    return web.Response(text="Bot is alive!", status=200)

if __name__ == "__main__":
    from aiogram.utils.executor import Executor
    executor = Executor(dp)
    executor._web_app.router.add_get("/", health)

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
