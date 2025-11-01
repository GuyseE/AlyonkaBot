from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from datetime import datetime, timedelta
import json, os, random

# -----------------------------------------
# 🔒 Безопасная загрузка токена
# -----------------------------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в переменные окружения на Koyeb.")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# -----------------------------------------
# 🗂 Хелперы для хранения данных
# -----------------------------------------
def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def user_file(uid: int, stem: str) -> str:
    return f"{stem}_{uid}.json"

def get_status(uid: int) -> dict:
    return _load(user_file(uid, "status"), {})

def save_status(uid: int, data: dict):
    _save(user_file(uid, "status"), data)

def get_coupon(uid: int) -> dict:
    return _load(user_file(uid, "coupon"), {})

def save_coupon(uid: int, data: dict):
    _save(user_file(uid, "coupon"), data)

# -----------------------------------------
# 📅 План питания
# -----------------------------------------
plan = _load("plan.json", {
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
})
edit_state = {}

# -----------------------------------------
# 💬 Комплименты (30)
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
        KeyboardButton("📝 Редактировать план"),
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

def edit_day_kb(day: str):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Добавить блюдо", callback_data=f"addmeal|{day}"),
        InlineKeyboardButton("🗑 Удалить блюдо", callback_data=f"delmeal|{day}"),
    )
    return kb

# -----------------------------------------
# 🚀 Команды
# -----------------------------------------
@dp.message_handler(commands=["start", "меню"])
async def cmd_start(msg: types.Message):
    await msg.answer("Привет, любимая 🤍\nКнопки всегда рядом и удобно!", reply_markup=bottom_menu())

# ❤️
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

# ✅ / ❌ отметки
@dp.callback_query_handler(lambda c: c.data.startswith("done"))
async def cb_done(cq: types.CallbackQuery):
    uid = cq.from_user.id
    _, day, idx = cq.data.split("|")
    idx = int(idx)
    meal = plan[day][idx]
    st = get_status(uid)
    st[f"{day}|{meal}"] = "✅"
    save_status(uid, st)
    await cq.message.edit_text(f"✅ Молодец, ты съела — {meal}!\n\n{random.choice(compliments)}", reply_markup=meal_kb(day, idx))
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
    await cq.message.edit_text(f"❌ Ты пропустила!! Надо НАКАЗАТЬ....) Но я все равно дуже люблю тебя 🤍", reply_markup=meal_kb(day, idx))
    await cq.answer("Отмечено ❌")

# -----------------------------------------
# 📊 Статус
# -----------------------------------------
@dp.message_handler(lambda m: m.text == "📊 Статус")
async def show_status(msg: types.Message):
    uid = msg.from_user.id
    st = get_status(uid)
    items = []
    for key, mark in st.items():
        day, meal = key.split("|", 1)
        if day in plan and meal in plan[day]:
            items.append((day, meal, mark))
    if not items:
        await msg.answer("Пока нет отметок 😇", reply_markup=bottom_menu())
        return
    text = "📋 <b>Статус:</b>\n"
    for day, meal, mark in items:
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
            left = 7 - (now - last).days
            await msg.answer(f"❌ Купон уже активирован ( йолки палки надо ждать )", reply_markup=bottom_menu())
            return
    data["last"] = now.isoformat()
    save_coupon(uid, data)
    await msg.answer("🎟 Насладись этим купоном! 🍫\nТы заслужила 🤍", reply_markup=bottom_menu())

# -----------------------------------------
# 📝 Редактирование плана
# -----------------------------------------
@dp.message_handler(lambda m: m.text == "📝 Редактировать план")
async def edit_menu(msg: types.Message):
    kb = InlineKeyboardMarkup()
    for d in plan:
        kb.add(InlineKeyboardButton(d, callback_data=f"editday|{d}"))
    kb.add(InlineKeyboardButton("➕ Добавить новый день", callback_data="newday"))
    await msg.answer("Выбери день для редактирования:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "newday")
async def cb_newday(cq: types.CallbackQuery):
    edit_state[cq.from_user.id] = {"mode": "newday"}
    await cq.message.answer("Введи название нового дня:")

@dp.message_handler(lambda m: m.from_user.id in edit_state and edit_state[m.from_user.id].get("mode") == "newday")
async def save_new_day(msg: types.Message):
    day = msg.text.capitalize().strip()
    if not day:
        await msg.answer("Пустое название не принимаю 🙂")
        return
    plan.setdefault(day, [])
    _save("plan.json", plan)
    del edit_state[msg.from_user.id]
    await msg.answer(f"Создан новый день: {day} ✅", reply_markup=bottom_menu())

@dp.callback_query_handler(lambda c: c.data.startswith("editday"))
async def cb_editday(cq: types.CallbackQuery):
    _, day = cq.data.split("|")
    edit_state[cq.from_user.id] = {"day": day}
    await cq.message.answer(f"Редактирование дня {day}", reply_markup=edit_day_kb(day))

@dp.callback_query_handler(lambda c: c.data.startswith("addmeal"))
async def cb_addmeal(cq: types.CallbackQuery):
    _, day = cq.data.split("|")
    edit_state[cq.from_user.id] = {"day": day, "mode": "add"}
    await cq.message.answer(f"Напиши новое блюдо для {day}:")

@dp.message_handler(lambda m: m.from_user.id in edit_state and edit_state[m.from_user.id].get("mode") == "add")
async def save_meal(msg: types.Message):
    state = edit_state[msg.from_user.id]
    day = state["day"]
    txt = msg.text.strip()
    if txt:
        plan[day].append(txt)
        _save("plan.json", plan)
        await msg.answer(f"Добавлено новое блюдо в {day} ✅", reply_markup=bottom_menu())
    del edit_state[msg.from_user.id]

@dp.callback_query_handler(lambda c: c.data.startswith("delmeal"))
async def cb_delmeal(cq: types.CallbackQuery):
    _, day = cq.data.split("|")
    meals = plan.get(day, [])
    if not meals:
        await cq.answer("Нет блюд для удаления", show_alert=True)
        return
    kb = InlineKeyboardMarkup()
    for i, meal in enumerate(meals):
        kb.add(InlineKeyboardButton(meal[:48], callback_data=f"dodel|{day}|{i}"))
    await cq.message.answer("Выбери блюдо для удаления:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("dodel"))
async def cb_dodel(cq: types.CallbackQuery):
    uid = cq.from_user.id
    _, day, idx = cq.data.split("|")
    idx = int(idx)
    if 0 <= idx < len(plan[day]):
        meal = plan[day].pop(idx)
        _save("plan.json", plan)
        st = get_status(uid)
        k = f"{day}|{meal}"
        if k in st:
            del st[k]
            save_status(uid, st)
        await cq.message.edit_text(f"❌ Удалено: {meal}")
        await cq.answer("Удалено ✅")
    else:
        await cq.answer("Не найдено", show_alert=True)

# -----------------------------------------
# ▶️ Запуск
# -----------------------------------------
if __name__ == "__main__":
    print("🚀 Бот запущен и работает 24/7")
    executor.start_polling(dp)
