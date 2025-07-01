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

# Vaqtlar (09:00-21:00)
times = [f"{hour:02d}:00" for hour in range(9, 22)]
booked_slots = {}

# CSV ga bandlov saqlash
def save_booking_to_csv(user_id, service, date, time):
    file_exists = os.path.isfile("bookings.csv")
    with open("bookings.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["user_id", "service", "date", "time", "timestamp"])
        writer.writerow([user_id, service, date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def get_main_menu():
    return ReplyKeyboardMarkup(
        [["/book"], ["/cabinet"], ["/cancel"], ["/admin"], ["/referal"], ["/cashback"],
         ["/instagram", "/telegram"], ["/location", "📍 Manzil"], ["/help"], ["📋 Xizmat turlari"]],
        resize_keyboard=True
    )

def get_back_button():
    return ReplyKeyboardMarkup([["\ud83d\udd19 Orqaga / Назад"]], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        referrer_id = args[0]
        user_id = str(update.effective_user.id)
        if user_id != referrer_id:
            referrals_data.setdefault(referrer_id, set()).add(user_id)
            cashback_data[referrer_id] = cashback_data.get(referrer_id, 0) + 5000
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
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
    await update.message.reply_text("📲 Telegram sahifamiz:\nhttps://t.me/barbershaxzod\n\nTelegram sahifamizga obuna bo‘ling!")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Instagram sahifamiz:\nhttps://www.instagram.com/barber_shaxzod\n\nInstagram sahifamizga obuna bo‘ling!")

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=41.220263, longitude=69.196518)
    await update.message.reply_text("📍 Manzilimiz: Toshkent, Sergeli tumani, Xiyobon ko‘chasi 25-uy")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam: Har qanday savol uchun admin bilan bog‘laning yoki /start buyrug‘ini bosing.")

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    buttons = [[s] for s in services]
    await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["\ud83d\udd19 Orqaga / Назад"]], resize_keyboard=True))

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
        context.user_data["selected_service"] = service
        buttons = [[d] for d in get_next_dates()]
        await update.message.reply_text(f"✅ Siz tanladingiz: {service}\n\n🗕 Iltimos, sanani tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["\ud83d\udd19 Orqaga / Назад"]], resize_keyboard=True))

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    if date in get_next_dates():
        context.user_data["selected_date"] = date
        service = context.user_data.get("selected_service")
        busy_times = booked_slots.get(date, {}).get(service, set())
        time_buttons = []
        for t in times:
            label = f"{t} ❌ Band" if t in busy_times else t
            time_buttons.append([label])
        await update.message.reply_text(f"🗕 Sana tanlandi: {date}\n\n🕒 Iltimos, vaqtni tanlang:", reply_markup=ReplyKeyboardMarkup(time_buttons + [["\ud83d\udd19 Orqaga / Назад"]], resize_keyboard=True))

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text.replace(" ❌ Band", "")
    service = context.user_data.get("selected_service")
    date = context.user_data.get("selected_date")
    user_id = update.effective_user.id

    if not service or not date:
        await update.message.reply_text("Iltimos, avval xizmat va sanani tanlang.")
        return

    busy = booked_slots.setdefault(date, {}).setdefault(service, set())
    if time in busy:
        await update.message.reply_text("❌ Bu vaqt allaqachon band. Iltimos, boshqa vaqt tanlang.")
        return

    existing = user_bookings.get(user_id)
    if existing and not existing.get("cancelled"):
        await update.message.reply_text("❌ Sizda mavjud bandlov bor. Avval bekor qiling yoki kuting.")
        return

    busy.add(time)
    user_bookings[user_id] = {
        "service": service, "date": date, "time": time,
        "cancelled": False, "cancel_count": existing.get("cancel_count", 0) if existing else 0,
        "last_cancel": existing.get("last_cancel") if existing else None
    }

    save_booking_to_csv(user_id, service, date, time)

    booking_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    remind_time = booking_datetime - timedelta(hours=1)
    now = datetime.now()
    if remind_time > now:
        wait_seconds = (remind_time - now).total_seconds()
        asyncio.create_task(schedule_reminder(update, context, wait_seconds, booking_datetime.strftime("%H:%M")))

    await update.message.reply_text(f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {service}\n🗕 Sana: {date}\n🕒 Vaqt: {time}", reply_markup=get_main_menu())

async def schedule_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, delay: float, time_str: str):
    await asyncio.sleep(delay)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"⏰ Eslatma: Siz bugun soat {time_str} da bandlovingiz bor. Iltimos, vaqtida yetib keling!"
    )

async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking = user_bookings.get(user_id)
    booking_info = f"📋 {booking['service']}\n🗕 {booking['date']}\n🕒 {booking['time']}" if booking and not booking.get("cancelled") else "Bandlov mavjud emas."
    cashback = cashback_data.get(str(user_id), 0)
    invites = len(referrals_data.get(str(user_id), []))
    await update.message.reply_text(f"👤 Shaxsiy kabinet:\n\n{booking_info}\n💰 Cashback: {cashback} so'm\n👥 Taklif qilganlar: {invites} ta")

async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking = user_bookings.get(user_id)
    if booking:
        last_cancel = booking.get("last_cancel")
        if booking.get("cancel_count", 0) >= 1:
            if last_cancel and (datetime.now() - last_cancel) < timedelta(hours=24):
                await update.message.reply_text("❌ Siz faqat 1 marta bandlovni bekor qilishingiz mumkin (24 soatda bir marta).")
                return

        booked_slots[booking['date']][booking['service']].discard(booking['time'])
        booking["cancelled"] = True
        booking["cancel_count"] = 1
        booking["last_cancel"] = datetime.now()
        await update.message.reply_text("✅ Bandlov bekor qilindi.", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("Sizda bandlov mavjud emas.")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz.")
        return
    stats = f"👥 Foydalanuvchilar: {len(user_bookings)}\n🗕 Bandlovlar: {sum(len(v) for v in booked_slots.values())}"
    await update.message.reply_text(f"🔧 Admin panel:\n{stats}")

async def handle_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bosh menyuga qaytdingiz.", reply_markup=get_main_menu())

app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("book", book))
app.add_handler(CommandHandler("cabinet", cabinet))
app.add_handler(CommandHandler("cancel", cancel_booking))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("referal", referal))
app.add_handler(CommandHandler("cashback", referal))
app.add_handler(CommandHandler("location", location))
app.add_handler(CommandHandler("instagram", instagram))
app.add_handler(CommandHandler("telegram", telegram))
app.add_handler(CommandHandler("help", help_command))

app.add_handler(MessageHandler(filters.TEXT & filters.Regex(service_pattern), choose_service))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^.*(09|10|11|12|13|14|15|16|17|18|19|20|21):00.*$"), choose_time))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Xizmat turlari$"), handle_services_button))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 Orqaga / Назад$"), back_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📍 Manzil$"), location))

app.run_polling()
