from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio
import csv
import os

# Admin ID
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

# Referrallar, cashback, bandlovlar
referrals_data = {}
cashback_data = {}
user_bookings = {}
user_cancel_limits = {}

# Xizmatlar ro'yxati
services = [
    "Soch olish", "Soqol olish", "Soqol togirlash", "Okantovka qilish",
    "Ukladka qlish", "Soch boyash", "Soqol boyash", "Yuzga maska qlish",
    "Yuz chiskasi", "Kuyov soch"
]

# Yordamchi tugma
SELECT_DONE = "✅ Tanlash tugadi"


def get_next_dates(num_days=7):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

# Vaqtlar (09:00-21:00)
times = [f"{hour:02d}:00" for hour in range(9, 22)]
booked_slots = {}

# CSV ga bandlov saqlash
def save_booking_to_csv(user_id, services, date, time):
    file_exists = os.path.isfile("bookings.csv")
    with open("bookings.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["user_id", "service", "date", "time", "timestamp"])
        writer.writerow([user_id, ", ".join(services), date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

# Menyu
def get_main_menu():
    return ReplyKeyboardMarkup(
        [["/book"], ["/cabinet"], ["/cancel"], ["/admin"], ["/referal"], ["/cashback"], ["/instagram", "/telegram"], ["/location"], ["/help"], ["📋 Xizmat turlari"]],
        resize_keyboard=True
    )

def get_back_button():
    return ReplyKeyboardMarkup([["🔙 Orqaga / Назад"]], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        referrer_id = args[0]
        user_id = str(update.effective_user.id)
        if user_id != referrer_id:
            referrals_data.setdefault(referrer_id, set()).add(user_id)
            cashback_data[referrer_id] = cashback_data.get(referrer_id, 0) + 5000
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇\n\nTelegram va Instagram sahifamizga obuna bo‘ling!",
        reply_markup=get_main_menu()
    )

async def referal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    invited_count = len(referrals_data.get(user_id, []))
    cashback = cashback_data.get(user_id, 0)
    await update.message.reply_text(
        f"🔗 Sizning taklif havolangiz: {referral_link}\n👥 Taklif qilgan do‘stlaringiz soni: {invited_count} ta\n💰 Cashback: {cashback} so'm"
    )

async def telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Telegram sahifamiz:\nhttps://t.me/barbershaxzod_uz\n\nTelegram va Instagram sahifamizga obuna bo‘ling!")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Instagram sahifamiz:\nhttps://www.instagram.com/barber_shaxzod\n\nTelegram va Instagram sahifamizga obuna bo‘ling!")

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=41.220263, longitude=69.196518)
    await update.message.reply_text("📍 Manzilimiz: Toshkent, Sergeli tumani, Xiyobon ko‘chasi 25-uy")

# <<< Ikkilamchi xizmatlar funksiyasi qo‘shildi >>>

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["selected_services"] = []
    buttons = [[s] for s in services] + [[SELECT_DONE]]
    await update.message.reply_text("📋 Xizmat turlarini tanlang (bir nechta tanlashingiz mumkin):", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service == SELECT_DONE:
        if not context.user_data["selected_services"]:
            await update.message.reply_text("Iltimos, hech bo‘lmasa bitta xizmat tanlang.")
            return
        buttons = [[d] for d in get_next_dates()]
        await update.message.reply_text("📅 Iltimos, sanani tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))
    elif service in services:
        selected = context.user_data["selected_services"]
        if service not in selected:
            selected.append(service)
        await update.message.reply_text(f"✅ Tanlanganlar: {', '.join(selected)}")

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    if date in get_next_dates():
        context.user_data["selected_date"] = date
        busy_times = booked_slots.get(date, {}).get(", ".join(context.user_data["selected_services"]), set())
        time_buttons = []
        for t in times:
            label = f"{t} ❌ Band" if t in busy_times else t
            time_buttons.append([label])
        await update.message.reply_text(f"📅 Sana tanlandi: {date}\n\n🕒 Iltimos, vaqtni tanlang:", reply_markup=ReplyKeyboardMarkup(time_buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))
