from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio
import csv
import os
import re

# Admin ID
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

# Referrallar, cashback, bandlovlar
referrals_data = {}
cashback_data = {}
user_bookings = {}
booked_slots = {}

# Xizmatlar ro'yxati
services = [
    "Soch olish – 200 000 so'm (yoshlar: 150 000 so'm)",
    "Soqol olish – 70 000 so'm",
    "Soqol to‘g‘rilash – 70 000 so'm",
    "Okantovka qilish – 50 000 so'm",
    "Ukladka qilish – 100 000+ so'm",
    "Soch bo‘yash – 70 000 so'm",
    "Soqol bo‘yash – 50 000 so'm",
    "Yuzga maska qilish – 50 000+ so'm",
    "Yuz chiskasi – 200 000 so'm",
    "Kuyov sochi – 50$"
]

escaped_services = [re.escape(s) for s in services]
service_pattern = f"^({'|'.join(escaped_services)})$"

def get_next_dates(num_days=7):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

times = [f"{hour:02d}:00" for hour in range(9, 22)]

def save_booking_to_csv(user_id, service, date, time):
    file_exists = os.path.isfile("bookings.csv")
    with open("bookings.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["user_id", "service", "date", "time", "timestamp"])
        writer.writerow([user_id, service, date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def get_main_menu():
    return ReplyKeyboardMarkup(
        [["/book"], ["/cabinet"], ["/cancel"], ["/admin"], ["/referal"], ["/cashback"], ["/instagram", "/telegram"], ["/location"], ["/help"], ["📋 Xizmat turlari"], ["💈 Narxlar"]],
        resize_keyboard=True
    )

def get_back_button():
    return ReplyKeyboardMarkup([["🔙 Orqaga / Назад"]], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Xush kelibsiz!", reply_markup=get_main_menu()
    )

async def referal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔗 Sizning taklif havolangiz: ...")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam: ...")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Instagram sahifamiz: ...")

async def telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Telegram sahifamiz: ...")

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Manzilimiz: ...")

async def narxlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💈 Narxlar:", reply_markup=ReplyKeyboardMarkup([[s] for s in services], resize_keyboard=True))

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    context.user_data["selected_service"] = service
    context.user_data["step"] = "choose_service"
    buttons = [[d] for d in get_next_dates()]
    await update.message.reply_text(f"✅ Siz tanladingiz: {service}\n\n📅 Iltimos, sanani tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    context.user_data["selected_date"] = date
    context.user_data["step"] = "choose_date"
    service = context.user_data.get("selected_service")
    busy_times = booked_slots.get(date, {}).get(service, set())
    time_buttons = []
    for t in times:
        label = f"{t} ❌ Band" if t in busy_times else t
        time_buttons.append([label])
    await update.message.reply_text(f"📅 Sana tanlandi: {date}\n\n🕒 Iltimos, vaqtni tanlang:", reply_markup=ReplyKeyboardMarkup(time_buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step == "choose_date":
        context.user_data["step"] = "choose_service"
        buttons = [[s] for s in services]
        await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))
    elif step == "choose_service":
        context.user_data["step"] = "book"
        await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=ReplyKeyboardMarkup([[s] for s in services] + [["🔙 Orqaga / Назад"]], resize_keyboard=True))
    else:
        await update.message.reply_text("🏠 Bosh menyuga qaytdingiz.", reply_markup=get_main_menu())

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text.replace(" ❌ Band", "")
    service = context.user_data.get("selected_service")
    date = context.user_data.get("selected_date")
    user_id = update.effective_user.id

    busy = booked_slots.setdefault(date, {}).setdefault(service, set())
    busy.add(time)
    user_bookings[user_id] = {
        "service": service, "date": date, "time": time,
        "cancelled": False
    }

    save_booking_to_csv(user_id, service, date, time)

    await update.message.reply_text(f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {service}\n📅 Sana: {date}\n🕒 Vaqt: {time}", reply_markup=get_main_menu())

async def schedule_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, delay: float, time_str: str):
    await asyncio.sleep(delay)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"⏰ Eslatma: Siz bugun soat {time_str} da bandlovingiz bor. Iltimos, vaqtida yetib keling!"
    )

if __name__ == '__main__':
   app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("referal", referal))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cashback", referal))
    app.add_handler(CommandHandler("instagram", instagram))
    app.add_handler(CommandHandler("telegram", telegram))
    app.add_handler(CommandHandler("location", location))
    app.add_handler(CommandHandler("narxlar", narxlar))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(service_pattern), choose_service))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^.*(09|10|11|12|13|14|15|16|17|18|19|20|21):00.*$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 Orqaga / Назад$"), back_handler))

    app.run_polling()
