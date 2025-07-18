from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio
import csv
import os
import re

# Admin ID
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

# Bandlovlar
user_bookings = {}
user_cancel_limits = {}

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
booked_slots = {}

def save_booking_to_csv(user_id, service, date, time):
    file_exists = os.path.isfile("bookings.csv")
    with open("bookings.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["user_id", "service", "date", "time", "timestamp"])
        writer.writerow([user_id, service, date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            ["✂️ Xizmatlar", "👤 Kabinet"],
            ["📅 Bandlovni bekor qilish"],
            ["📸 Instagram", "📲 Telegram"],
            ["📍 Lokatsiya", "ℹ️ Yordam"]
        ],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
        reply_markup=get_main_menu()
    )

async def telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Telegram sahifamiz:\nhttps://t.me/barbershaxzod")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Instagram sahifamiz:\nhttps://www.instagram.com/barber_shaxzod")

async def google_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=41.306167, longitude=69.236028)
    text = (
        "📍 <b>Barber Shaxzod manzili:</b>\n\n"
        "🗺 <a href='https://maps.app.goo.gl/rSNBiU5V4uxBsCgB9'>Google xaritada ko‘rish</a>\n"
        "🏙 Bunyodkor shoh ko'chasi 8Д, 100097, Тоshkent,\n"
        "🕘 Ish vaqti: 09:00 - 21:00"
    )
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam uchun admin bilan bog‘laning: @barber_shaxzod")

async def xizmat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = "choose_service"
    buttons = [[s] for s in services]
    await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga"]], resize_keyboard=True))

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
        context.user_data["selected_service"] = service
        context.user_data["step"] = "choose_date"
        buttons = [[d] for d in get_next_dates()]
        await update.message.reply_text(
            f"✅ Siz tanladingiz: {service}\n📅 Sanani tanlang:",
            reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga"]], resize_keyboard=True)
        )

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    if date in get_next_dates():
        context.user_data["selected_date"] = date
        context.user_data["step"] = "choose_time"
        service = context.user_data.get("selected_service")
        busy_times = booked_slots.get(date, {}).get(service, set())
        buttons = []
        for t in times:
            label = f"{t} ❌" if t in busy_times else t
            buttons.append([label])
        await update.message.reply_text("🕒 Vaqtni tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga"]], resize_keyboard=True))

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["step"] = "done"
    time = update.message.text.replace(" ❌", "")
    service = context.user_data.get("selected_service")
    date = context.user_data.get("selected_date")
    user_id = update.effective_user.id

    if not service or not date:
        await update.message.reply_text("Avval xizmat va sanani tanlang.")
        return

    busy = booked_slots.setdefault(date, {}).setdefault(service, set())
    if time in busy:
        await update.message.reply_text("❌ Bu vaqt band. Boshqa vaqt tanlang.")
        return

    existing = user_bookings.get(user_id)
    if existing and not existing.get("cancelled"):
        await update.message.reply_text("❌ Sizda faol bandlov bor.")
        return

    busy.add(time)
    user_bookings[user_id] = {
        "service": service,
        "date": date,
        "time": time,
        "cancelled": False,
        "cancel_count": existing.get("cancel_count", 0) if existing else 0,
        "last_cancel": existing.get("last_cancel") if existing else None
    }

    save_booking_to_csv(user_id, service, date, time)

    await update.message.reply_text(f"✅ Bandlov yaratildi:\n📋 {service}\n📅 {date}\n🕒 {time}", reply_markup=get_main_menu())

async def bekor_qilish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking = user_bookings.get(user_id)
    if booking and not booking.get("cancelled"):
        last_cancel = booking.get("last_cancel")
        if booking.get("cancel_count", 0) >= 1 and last_cancel and (datetime.now() - last_cancel) < timedelta(hours=24):
            await update.message.reply_text("❌ 24 soatda faqat 1 marta bekor qilish mumkin.")
            return
        booked_slots[booking["date"]][booking["service"]].discard(booking["time"])
        booking["cancelled"] = True
        booking["cancel_count"] += 1
        booking["last_cancel"] = datetime.now()
        await update.message.reply_text("✅ Bandlov bekor qilindi.", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("Sizda bandlov mavjud emas.")

async def shaxsiy_kabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking = user_bookings.get(user_id)

    text = "<b>👤 Shaxsiy kabinet</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n"

    if booking and not booking.get("cancelled"):
        text += "<b>📋 Faol bandlov:</b>\n"
        text += f"• 🧾 Xizmat: <i>{booking['service']}</i>\n"
        text += f"• 📅 Sana: <i>{booking['date']}</i>\n"
        text += f"• 🕒 Vaqt: <i>{booking['time']}</i>\n"
    else:
        text += "<b>📋 Faol bandlov:</b>\n"
        text += "• Hech qanday bandlov mavjud emas.\n"

    text += "━━━━━━━━━━━━━━━━━━\n"
    text += "<b>💰 Cashback tizimi o‘chirib qo‘yilgan.</b>"

    await update.message.reply_text(text, parse_mode="HTML")

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step == "choose_time":
        context.user_data["step"] = "choose_date"
        buttons = [[d] for d in get_next_dates()]
        await update.message.reply_text("📅 Sanani tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga"]], resize_keyboard=True))
    elif step == "choose_date":
        context.user_data["step"] = "choose_service"
        buttons = [[s] for s in services]
        await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga"]], resize_keyboard=True))
    else:
        context.user_data.clear()
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=get_main_menu())

if __name__ == "__main__":
        app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xizmat", xizmat))
    app.add_handler(CommandHandler("shaxsiy_kabinet", shaxsiy_kabinet))
    app.add_handler(CommandHandler("bekor_qilish", bekor_qilish))
    app.add_handler(CommandHandler("instagram", instagram))
    app.add_handler(CommandHandler("telegram", telegram))
    app.add_handler(CommandHandler("location", google_location))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(service_pattern), choose_service))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^.*:00.*$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 Orqaga$"), back_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^✂️ Xizmatlar$"), xizmat))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^👤 Kabinet$"), shaxsiy_kabinet))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📅 Bandlovni bekor qilish$"), bekor_qilish))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📍 Lokatsiya$"), google_location))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📸 Instagram$"), instagram))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📲 Telegram$"), telegram))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^ℹ️ Yordam$"), help_command))

    app.run_polling()
