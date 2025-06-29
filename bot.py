from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio

# Admin ID (o'zgartiring o'zingizga moslashtirib)
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

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

# Band qilingan vaqtlar
booked_slots = {}

# Asosiy menyu
def get_main_menu():
    return ReplyKeyboardMarkup(
        [["/book"], ["/cabinet"], ["/cancel"], ["/admin"], ["/referal"], ["/cashback"], ["/instagram"], ["/location"], ["/help"], ["📋 Xizmat turlari"]],
        resize_keyboard=True
    )

# Orqaga (Назад) tugmasi
def get_back_button():
    return ReplyKeyboardMarkup([["🔙 Orqaga / Назад"]], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
        reply_markup=get_main_menu()
    )

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    service_buttons = [[s] for s in services] + [["🔙 Orqaga / Назад"]]
    reply_markup = ReplyKeyboardMarkup(service_buttons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=reply_markup)

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service == "🔙 Orqaga / Назад":
        await start(update, context)
        return
    if service in services:
        context.user_data.clear()
        context.user_data["selected_service"] = service
        dates = get_next_dates()
        date_buttons = [[d] for d in dates] + [["🔙 Orqaga / Назад"]]
        reply_markup = ReplyKeyboardMarkup(date_buttons, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"✅ Siz tanladingiz: {service}\n\nEndi xizmat uchun kunni tanlang:", reply_markup=reply_markup)

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_date = update.message.text
    if selected_date == "🔙 Orqaga / Назад":
        await book(update, context)
        return
    if selected_date in get_next_dates():
        context.user_data["selected_date"] = selected_date
        selected_service = context.user_data.get("selected_service")
        global_slots = booked_slots.setdefault("global", {}).setdefault(selected_service, {})
        busy_times = global_slots.get(selected_date, [])
        time_buttons = []
        for t in times:
            if t in busy_times:
                time_buttons.append([f"{t} ❌ Band / Занято"])
            else:
                time_buttons.append([t])
        time_buttons.append(["🔙 Orqaga / Назад"])
        reply_markup = ReplyKeyboardMarkup(time_buttons, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"📅 Sana tanlandi: {selected_date}\n\nEndi vaqtni tanlang:", reply_markup=reply_markup)

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_time_raw = update.message.text
    if selected_time_raw == "🔙 Orqaga / Назад":
        await choose_date(update, context)
        return

    selected_date = context.user_data.get("selected_date")
    selected_service = context.user_data.get("selected_service", "Noma'lum")
    now = datetime.now()

    user_data = booked_slots.setdefault(user_id, {"last_change": None, "services": {}, "actions": {"cancelled": 0}})
    service_data = user_data["services"].setdefault(selected_service, {"count": 0, "dates": {}})

    if service_data["count"] >= 2:
        await update.message.reply_text(f"❗ Siz '{selected_service}' xizmatini 2 martadan ortiq band qila olmaysiz.", reply_markup=get_main_menu())
        return

    selected_time = selected_time_raw.split()[0]

    if selected_date and selected_time in times:
        global_service_slots = booked_slots.setdefault("global", {}).setdefault(selected_service, {})
        day_slots = global_service_slots.setdefault(selected_date, [])

        if selected_time in day_slots:
            await update.message.reply_text("❌ Kechirasiz, bu vaqt allaqachon band.", reply_markup=get_main_menu())
            return

        day_slots.append(selected_time)
        service_data["dates"][selected_date] = selected_time
        service_data["count"] += 1
        user_data["last_change"] = now

        # Eslatma yuborish uchun vaqt farqini hisoblash (bandlovdan 1 soat oldin yuborish)
        remind_time = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M") - timedelta(hours=1)
        delay_seconds = (remind_time - now).total_seconds()
        if delay_seconds > 0:
            asyncio.create_task(schedule_reminder(context, user_id, selected_service, selected_date, selected_time, delay_seconds))

        await update.message.reply_text(
            f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {selected_service}\n📅 Sana: {selected_date}\n🕒 Vaqt: {selected_time}\n\nTez orada siz bilan bog‘lanamiz!",
            reply_markup=get_main_menu()
        )

async def schedule_reminder(context, user_id, service, date, time, delay):
    await asyncio.sleep(delay)
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⏰ Eslatma: Sizning '{service}' xizmatiga bandlovingiz \n📅 {date} kuni, 🕒 {time} da.\n\nIltimos, kechikmang!"
        )
    except Exception as e:
        print(f"Eslatma yuborishda xatolik: {e}")

async def handle_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)

async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = booked_slots.get(user_id, {})
    services_info = user_data.get("services", {})
    cashback = "0 so'm"
    referrals = 0

    if not services_info:
        text = "📋 Sizda hali hech qanday bandlov mavjud emas."
    else:
        rows = []
        for service, info in services_info.items():
            for date, time in info.get("dates", {}).items():
                rows.append(f"• {service} - {date} {time}")
        text = "📋 Sizning bandlovlaringiz:\n" + "\n".join(rows)

    await update.message.reply_text(
        f"👤 Shaxsiy kabinet\n\n{text}\n\n💰 Keshbek: {cashback}\n👥 Taklif qilgan do‘stlaringiz: {referrals} ta"
    )

async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = booked_slots.get(user_id)
    if not user_data:
        await update.message.reply_text("❗ Sizda hech qanday bandlov mavjud emas.")
        return

    if user_data["actions"].get("cancelled", 0) >= 1:
        await update.message.reply_text("❌ Siz bandlovni faqat 1 marta bekor qilishingiz mumkin.")
        return

    service_data = user_data.get("services", {})
    if not service_data:
        await update.message.reply_text("❗ Bekor qilinadigan bandlov topilmadi.")
        return

    for service, info in service_data.items():
        for date, time in info.get("dates", {}).items():
            booked_time_list = booked_slots["global"][service][date]
            if time in booked_time_list:
                booked_time_list.remove(time)
    user_data["services"].clear()
    user_data["actions"]["cancelled"] += 1

    await update.message.reply_text("✅ Bandlovingiz bekor qilindi.", reply_markup=get_main_menu())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Sizda admin panelga kirish huquqi yo‘q.")
        return

    total_users = len([uid for uid in booked_slots.keys() if isinstance(uid, int)])
    total_bookings = sum(
        len(info.get("dates", {})) for u in booked_slots.values() if isinstance(u, dict)
        for info in u.get("services", {}).values()
    )

    await update.message.reply_text(
        f"👨‍💼 Admin Panel:\n\n👥 Foydalanuvchilar soni: {total_users}\n📅 Umumiy bandlovlar: {total_bookings}"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("cabinet", cabinet))
    app.add_handler(CommandHandler("cancel", cancel_booking))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(services)})$"), choose_service))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^.*(09|10|11|12|13|14|15|16|17|18|19|20|21):00.*$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Xizmat turlari$"), handle_services_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 Orqaga / Назад$"), start))

    app.run_polling()



