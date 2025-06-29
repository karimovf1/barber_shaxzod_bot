from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio

# Admin ID (o'zgartiring o'zingizga moslashtirib)
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

# Referrallar ma'lumotlari
referrals_data = {}
cashback_data = {}

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
            cashback_data[referrer_id] = cashback_data.get(referrer_id, 0) + 5000  # 5 ming so'm cashback
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

# Qo‘shimcha funksiyalar keyingi bosqichda kiritiladi (book, choose_service, choose_date, choose_time, cabinet, cancel_booking, admin va h.k.)

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




