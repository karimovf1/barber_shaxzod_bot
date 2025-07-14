from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import asyncio
import csv
import os
import re

# Admin ID
ADMIN_ID = 123456789

# Referrallar, cashback, bandlovlar
referrals_data = {}
cashback_data = {}
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

# START komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        referrer_id = args[0]
        user_id = str(update.effective_user.id)
        if user_id != referrer_id:
            referrals_data.setdefault(referrer_id, set()).add(user_id)
            cashback_data[referrer_id] = cashback_data.get(referrer_id, 0) + 5000

    text = (
        "Assalomu alaykum, <b>Barber Shaxzod</b> botiga xush kelibsiz!\n\n"
        "Quyidagi buyruqlardan foydalaning:\n\n"
        "<b>/xizmat</b> – Soch/salon xizmatlaridan birini tanlash\n"
        "<b>/shaxsiy_kabinet</b> – Shaxsiy ma'lumotlaringiz va bandlov holati\n"
        "<b>/bekor_qilish</b> – Faol bandlovni bekor qilish\n"
        "<b>/cashback</b> – Referal va cashback ma’lumotlari\n"
        "<b>/instagram</b> – Instagram sahifamizga o'tish\n"
        "<b>/telegram</b> – Telegram sahifamizga o'tish\n"
        "<b>/location</b> – Manzilimizni ko'rish\n"
        "<b>/help</b> – Yordam\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def xizmat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Xizmatlar ro'yxati:\n1. Soch olish\n2. Soqol olish\n...")

async def shaxsiy_kabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Bu sizning shaxsiy kabinetingiz.")

async def bekor_qilish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Bandlov bekor qilindi.")

async def cashback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Sizning cashback balansingiz: 0 so'm.")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Instagram: https://www.instagram.com/barber_shaxzod")

async def telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Telegram: https://t.me/barbershaxzod")

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=41.306167, longitude=69.236028)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam uchun admin: @barber_shaxzod")



# Qolgan komandalar (shaxsiy kabinet, cashback, xizmatlar, band qilish, bekor qilish va h.k.)
# Qisqartirilgan: shu yerga sening mavjud funksiyalaringni to'g'ridan-to'g'ri qo'shamiz
# Bu yerda faqat interfeys uchun asosiy o'zgarishlar berilgan

if __name__ == "__main__":
    app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xizmat", xizmat))
    app.add_handler(CommandHandler("shaxsiy_kabinet", shaxsiy_kabinet))
    app.add_handler(CommandHandler("bekor_qilish", bekor_qilish))
    app.add_handler(CommandHandler("cashback", cashback))
    app.add_handler(CommandHandler("instagram", instagram))
    app.add_handler(CommandHandler("telegram", telegram))
    app.add_handler(CommandHandler("location", location))
    app.add_handler(CommandHandler("help", help_command))

    # Qolgan komandalarni shu yerga joylashtirasiz:
    # /xizmat, /shaxsiy_kabinet, /bekor_qilish, /cashback, /telegram, /instagram, /location, /help

    app.run_polling()

# BotFather menyu:
# /start - Boshlash
# /xizmat - Xizmatlar ro'yxati
# /shaxsiy_kabinet - Shaxsiy kabinet
# /bekor_qilish - Bandlovni bekor qilish
# /cashback - Referal va cashback
# /instagram - Instagram sahifa
# /telegram - Telegram sahifa
# /location - Lokatsiya
# /help - Yordam
