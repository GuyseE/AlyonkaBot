from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from datetime import datetime, timedelta
import json, os, random

TOKEN = "8595502768:AAFPpYu0kZz3n7YPMDHjVsE4n20Ql8HeC3w"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ---------- helpers: storage ----------
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

# ---------- ПЛАН ----------
plan = _load("plan.json", {
    "Воскресенье": [
        "завтрак — омлет из одного яйца, сосиска варёная, 40 г гречки + огурчик",
        "обед — рис и красная рыбка в сливках, на десерт яблочко",
        "ужин — салат с курицей, 40 г пасты и сыром",
    ],
    "Понедельник": [
        "завтрак — омлет из одного яйца + 1 белок, варёная сосиска, 40 г мягкой овсянки (на воде или овсяном молоке), немного банана",
        "обед — картофельное пюре с куриным филе или индейкой, мягкие тушёные овощи (морковь, кабачок), на десерт яблочко",
        "ужин — рисовая лапша с мелко нарезанной курицей и мягкими овощами, чай ромашковый или мятный",
    ],
})
edit_state = {}  # per-user editing state

# ---------- compliments (30) ----------
compliments = [
    "Когда ты рядом, даже молчание становится самым громким звуком в мире.",
    "Ты не просто красивая, у тебя внутри целая буря, и я хочу тонуть в ней.",
    "От тебя веет чем-то настоящим, таким, что не сыграть и не подделать.",
    "В тебе слишком много реальности, чтобы быть просто сном.",
    "Ты как запах детства, который вдруг вернулся, и внутри усьо сжалось от тепла.",
    "Когда ты смотришь, мне хочется замереть, чтобы не спугнуть этот момент.",
    "Я не знаю, что ты со мной сделала, но внутри стало светло и тихо одновременно.",
    "В твоей усталости есть что-то прекрасное, ты даже в разбитом состоянии настоящая.",
    "Ты умеешь смотреть так, будто видишь все, что я прячу от самого себя.",
    "Мне не нужен идеальный мир, если в нем нет твоего дыхания.",
    "У тебя такая энергетика, что даже звезды могли бы питаться тобой.",
    "Иногда ты просто говоришь что-то обычное, а у меня внутри все рушится и заново собирается.",
    "Ты не похожа на тех, кого можно забыть. Ты врезаешься в память, как ожог.",
    "Мне нравится, как ты можешь быть нежной и острой в одно мгновение.",
    "Ты тот человек, рядом с которым тишина становится безопасной.",
    "Ты не светишься, ты горишь, и я тянусь к этому огню, даже если обожгусь.",
    "Когда ты улыбаешься, будто время делает шаг назад, чтобы просто посмотреть.",
    "У тебя внутри столько силы, что рядом с тобой мир выпрямляется.",
    "Твоя хрупкость не слабость, это искусство быть живой.",
    "Я не могу объяснить, но когда ты рядом, даже воздух будто узнаёт тебя.",
    "Ты редкость, из тех, кого мир делает один раз и больше не повторяет.",
    "Есть люди, после которых остаётся пустота, а после тебя свет.",
    "Ты умеешь быть настоящей даже в хаосе, и это сводит с ума.",
    "Когда ты просто дышишь рядом, будто сердце начинает играть мелодию, которую я давно забыл.",
    "Если бы чувства имели цвет, ты была бы всем спектром сразу.",
    "Тебя не хочется трогать, тебя хочется чувствовать.",
    "Когда я думаю о тебе, будто что-то внутри становится мягче, теплее, глубже.",
    "Ты не просто вошла в мою жизнь, ты вросла в нее.",
    "Тебя невозможно понять до конца, и именно это делает тебя бесконечной.",
    "Даже если бы я умел писать идеальные слова, они все равно не догнали бы то, что я чувствую рядом с тобой.",
]

love_phrases = [
    "я тебя тоже безумно люблю!! 💞",
    "а помнишь 12 января , наши первые вебочки? 🥹",
    "все, что у меня есть , твое тепло 💗",
    "я счастлив, что именно ТЫ моя 💖",
    "ты , мой дом, мое спокойствие, мое все 🤍",
    "я бы сейчас обнял тебя так крепко, чтобы ты почувствовала усьо💞",
    "с каждым днем люблю тебя все сильнее 🌙",
    "ты!! причина, почему я улыбаюсь даже ночью 💫",
    "я помню наш первый вечер, каждое слово, каждую улыбку 💭",
    "ты навсегда в моем сердце, Альонка 🤍",
]

# ---------- keyboards ----------
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

# ---------- start / menu ----------
@dp.message_handler(commands=["start", "меню"])
async def cmd_start(msg: types.Message):
    await msg.answer(
        "Привет, любимая 🤍\nКпноки всегда рядом и удобно!",
        reply_markup=bottom_menu()
    )

# ---------- love button ----------
@dp.message_handler(lambda m: m.text == "🤍 Я ЛЮБЛЮ ТЕБЯ 🤍")
async def love_btn(msg: types.Message):
    await msg.answer(random.choice(love_phrases))

# ---------- show day with per-meal buttons ----------
@dp.message_handler(lambda m: m.text and m.text.capitalize() in plan)
async def show_day(msg: types.Message):
    day = msg.text.capitalize()
    meals = plan.get(day, [])
    await msg.answer(f"🍽 План на {day}:", reply_markup=bottom_menu())
    if not meals:
        await msg.answer("Пока шо ничо немаа")
        return

    st = get_status(msg.from_user.id)
    for i, meal in enumerate(meals):
        mark = st.get(f"{day}|{meal}", "")
        prefix = "✅" if mark == "✅" else "❌" if mark == "❌" else "•"
        await msg.answer(f"{prefix} {meal}", reply_markup=meal_kb(day, i))

# ---------- mark done/missed (keeps buttons) ----------
@dp.callback_query_handler(lambda c: c.data.startswith("done"))
async def cb_done(cq: types.CallbackQuery):
    uid = cq.from_user.id
    _, day, idx = cq.data.split("|")
    idx = int(idx)
    meal = plan[day][idx]
    st = get_status(uid)
    st[f"{day}|{meal}"] = "✅"
    save_status(uid, st)
    text = f"✅ Молодец, ты съела — {meal}!\n\n{random.choice(compliments)}"
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
    text = (
        f"❌ Ты пропустила... {meal}!\n\n"
        "😤 И НЕ стыдно?!\n"
        "💥 Жди наказания....) но я все равно тебя безумно люблю 🤍"
    )
    await cq.message.edit_text(text, parse_mode="HTML", reply_markup=meal_kb(day, idx))
    await cq.answer("Отмечено ❌")

# ---------- status ----------
@dp.message_handler(lambda m: m.text == "📊 Статус")
@dp.message_handler(commands=["статус"])
async def show_status(msg: types.Message):
    uid = msg.from_user.id
    st = get_status(uid)
    # фильтруем удалённые блюда
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

# ---------- coupon ----------
@dp.message_handler(lambda m: m.text == "🎟 Купон на вредность")
async def coupon(msg: types.Message):
    uid = msg.from_user.id
    data = get_coupon(uid)
    now = datetime.now()
    if "last" in data:
        last = datetime.fromisoformat(data["last"])
        if now - last < timedelta(days=7):
            left = 7 - (now - last).days
            await msg.answer(f"❌ Купон уже активировала (жди йолки палки)! Осталось {left} дн.", reply_markup=bottom_menu())
            return
    data["last"] = now.isoformat()
    save_coupon(uid, data)
    await msg.answer(
        "🎟 Насладись этим купоном!!!  🍫\nИногда можно и ты старалась 🤍\n"
        "Но помни каждый раз соблюдаешь режим = комплимент!  ✨",
        reply_markup=bottom_menu()
    )

# ---------- editing ----------
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
        # чистим статус только у текущего пользователя (его вид)
        st = get_status(uid)
        k = f"{day}|{meal}"
        if k in st:
            del st[k]
            save_status(uid, st)
        await cq.message.edit_text(f"❌ Удалено: {meal}")
        await cq.answer("Удалено ✅")
    else:
        await cq.answer("Не найдено", show_alert=True)

# ---------- run ----------
if __name__ == "__main__":
    executor.start_polling(dp)
