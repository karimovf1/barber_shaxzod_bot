from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio

# Admin ID (o'zgartiring o'zingizga moslashtirib)
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

# Referrallar ma'lumotlari
referrals_data = {}
cashback_data = {}

# Bandlovlar tarixi va cheklovlar
user_bookings = {}
user_booking_limits = {}
user_cancel_limits = {}

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

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today_str = datetime.now().strftime("%Y-%m-%d")
    if user_booking_limits.get(user_id, {}).get(today_str, 0) >= 2:
        await update.message.reply_text("❌ Siz bugun ikki marta bandlov kiritgansiz. Iltimos, ertaga urinib ko‘ring.")
        return
    context.user_data.clear()
    buttons = [[s] for s in services]
    await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
        context.user_data["selected_service"] = service
        buttons = [[d] for d in get_next_dates()]
        await update.message.reply_text(f"✅ Siz tanladingiz: {service}\n\n📅 Iltimos, sanani tanlang:", reply_markup=ReplyKeyboardMarkup(buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))

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
        await update.message.reply_text(f"📅 Sana tanlandi: {date}\n\n🕒 Iltimos, vaqtni tanlang:", reply_markup=ReplyKeyboardMarkup(time_buttons + [["🔙 Orqaga / Назад"]], resize_keyboard=True))

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
        await update.message.reply_text("❌ Bu vaqt allaqachon band qilingan. Iltimos, boshqa vaqt tanlang.")
        return

    # Bandlovni saqlash
    busy.add(time)
    user_bookings[user_id] = {"service": service, "date": date, "time": time}
    today_str = datetime.now().strftime("%Y-%m-%d")
    user_booking_limits.setdefault(user_id, {})[today_str] = user_booking_limits.get(user_id, {}).get(today_str, 0) + 1
    user_cancel_limits.setdefault(user_id, {})[today_str] = 0

    await update.message.reply_text(f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {service}\n📅 Sana: {date}\n🕒 Vaqt: {time}\n\nTez orada siz bilan bog‘lanamiz!", reply_markup=get_main_menu())

async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking = user_bookings.get(user_id)
    booking_info = f"📋 {booking['service']}\n📅 {booking['date']}\n🕒 {booking['time']}" if booking else "Hozircha bandlov mavjud emas."
    cashback = cashback_data.get(str(user_id), 0)
    invites = len(referrals_data.get(str(user_id), []))
    await update.message.reply_text(f"👤 Shaxsiy kabinet:\n\n📅 Bandlov: {booking_info}\n💰 Cashback: {cashback} so'm\n👥 Taklif qilganlar soni: {invites} ta")

async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today_str = datetime.now().strftime("%Y-%m-%d")
    cancels_today = user_cancel_limits.get(user_id, {}).get(today_str, 0)

    if cancels_today >= 1:
        await update.message.reply_text("❌ Siz bugun faqat 1 marta bandlovni bekor qilishingiz mumkin.")
        return

    booking = user_bookings.get(user_id)
    if booking:
        booked_slots[booking['date']][booking['service']].discard(booking['time'])
        del user_bookings[user_id]
        user_cancel_limits.setdefault(user_id, {})[today_str] = cancels_today + 1
        await update.message.reply_text("✅ Bandlovingiz bekor qilindi.", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("Sizda mavjud bandlov topilmadi.")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz.")
        return
    stats = f"👥 Jami foydalanuvchilar: {len(user_bookings)}\n📅 Jami bandlovlar: {sum(len(v) for v in booked_slots.values())}"
    await update.message.reply_text(f"🔧 Admin panel:\n{stats}")

async def handle_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)

if __name__ == '__main__':
    app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("cabinet", cabinet))
    app.add_handler(CommandHandler("cancel", cancel_booking))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("referal", referal))
    app.add_handler(CommandHandler("cashback", referal))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(services)})$"), choose_service))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^.*(09|10|11|12|13|14|15|16|17|18|19|20|21):00.*$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Xizmat turlari$"), handle_services_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔙 Orqaga / Назад$"), start))

    app.run_polling()
