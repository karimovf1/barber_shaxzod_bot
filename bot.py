from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta

# Xizmatlar ro'yxati
services = [
    "Soch olish", "Soqol olish", "Soqol togirlash", "Okantovka qilish",
    "Ukladka qlish", "Soch boyash", "Soqol boyash", "Yuzga maska qlish",
    "Yuz chiskasi", "Kuyov soch"
]

# Sana generatori (7 kunlik)
def get_next_dates(num_days=7):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

# Vaqtlar ro'yxati (09:00 - 21:00)
times = [f"{hour:02d}:00" for hour in range(9, 22)]

# Band qilingan vaqtlar (xotirada saqlanadi)
booked_slots = {}  # {user_id: {"last_change": datetime, "dates": {"2025-06-28": "10:00"}}}

# Asosiy menyu
def get_main_menu():
    return ReplyKeyboardMarkup(
        [["/book"], ["/cabinet"], ["/cancel"], ["/referal"], ["/cashback"], ["/instagram"], ["/location"], ["/help"], ["📋 Xizmat turlari"]],
        resize_keyboard=True
    )

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
        reply_markup=get_main_menu()
    )

# /book komandasi
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    service_buttons = [[s] for s in services]
    reply_markup = ReplyKeyboardMarkup(service_buttons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=reply_markup)

# Xizmat tanlash
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
        context.user_data.clear()
        context.user_data["selected_service"] = service
        dates = get_next_dates()
        date_buttons = [[d] for d in dates]
        reply_markup = ReplyKeyboardMarkup(date_buttons, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"✅ Siz tanladingiz: {service}\n\nEndi xizmat uchun kunni tanlang:", reply_markup=reply_markup)

# Sana tanlash
async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_date = update.message.text
    if selected_date in get_next_dates():
        context.user_data["selected_date"] = selected_date
        global_slots = booked_slots.setdefault("global", {})
        busy_times = global_slots.get(selected_date, [])
        time_buttons = []
        for t in times:
            if t in busy_times:
                time_buttons.append([f"{t} ❌ Band / Занято"])
            else:
                time_buttons.append([t])
        reply_markup = ReplyKeyboardMarkup(time_buttons, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"📅 Sana tanlandi: {selected_date}\n\nEndi vaqtni tanlang:", reply_markup=reply_markup)

# Vaqt tanlash
async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_time_raw = update.message.text
    selected_date = context.user_data.get("selected_date")
    selected_service = context.user_data.get("selected_service", "Noma'lum")
    now = datetime.now()

    user_data = booked_slots.setdefault(user_id, {"last_change": None, "dates": {}})
    if user_data["last_change"] and (now - user_data["last_change"]).total_seconds() < 86400:
        await update.message.reply_text("Siz 24 soat ichida faqat bir marta bandlovni o'zgartirishingiz mumkin. Iltimos, keyinroq urinib ko‘ring.", reply_markup=get_main_menu())
        return

    selected_time = selected_time_raw.split()[0]

    if selected_date and selected_time in times:
        global_slots = booked_slots.setdefault("global", {})
        day_slots = global_slots.setdefault(selected_date, [])

        if selected_time in day_slots:
            await update.message.reply_text("Kechirasiz, bu vaqt allaqachon band.", reply_markup=get_main_menu())
            return

        day_slots.append(selected_time)
        user_data["dates"][selected_date] = selected_time
        user_data["last_change"] = now

        await update.message.reply_text(
            f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {selected_service}\n📅 Sana: {selected_date}\n🕒 Vaqt: {selected_time}\n\nTez orada siz bilan bog‘lanamiz!",
            reply_markup=get_main_menu()
        )

# Bandlovni bekor qilish
async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = booked_slots.get(user_id)

    if not user_data or not user_data.get("dates"):
        await update.message.reply_text("Sizda bekor qilinadigan bandlov mavjud emas.", reply_markup=get_main_menu())
        return

    cancelled_texts = []
    for date, time in user_data["dates"].items():
        global_day_slots = booked_slots.get("global", {}).get(date, [])
        if time in global_day_slots:
            global_day_slots.remove(time)
        cancelled_texts.append(f"📅 {date} 🕒 {time}")

    user_data["dates"] = {}
    user_data["last_change"] = None

    await update.message.reply_text(
        "🚫 Quyidagi bandlov(lar) bekor qilindi:\n\n" + "\n".join(cancelled_texts),
        reply_markup=get_main_menu()
    )

# 📋 Xizmat turlari tugmasi bosilganda
async def handle_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)

# /cabinet komandasi
async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = booked_slots.get(user_id, {})
    booking_info = user_data.get("dates", {})
    if not booking_info:
        booking_history = "Hozircha hech qanday bandlov mavjud emas."
    else:
        booking_history = "\n".join([f"{date} - {time}" for date, time in booking_info.items()])
    cashback_amount = "0 so'm"
    referral_count = 0
    text = (
        f"👤 Shaxsiy kabinet:\n\n"
        f"📅 Bandlovlar tarixi:\n{booking_history}\n\n"
        f"💰 Keshbek: {cashback_amount}\n"
        f"👥 Taklif qilgan do‘stlaringiz: {referral_count} ta"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu())

# === BOTNI ISHGA TUSHIRISH ===
if __name__ == '__main__':
    app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("cabinet", cabinet))
    app.add_handler(CommandHandler("cancel", cancel_booking))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(services)})$"), choose_service))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^.*(09|10|11|12|13|14|15|16|17|18|19|20|21):00.*$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Xizmat turlari$"), handle_services_button))

    app.run_polling()








