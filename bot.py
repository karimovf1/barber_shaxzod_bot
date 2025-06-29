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

# Vaqtlar ro'yxati
times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/book"], ["/cabinet"], ["/referal"], ["/cashback"], ["/instagram"], ["/location"], ["/help"], ["📋 Xizmat turlari"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
        reply_markup=reply_markup
    )

# /book komandasi
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service_buttons = [[s] for s in services]
    reply_markup = ReplyKeyboardMarkup(service_buttons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📋 Xizmat turini tanlang:", reply_markup=reply_markup)

# Xizmat tanlash
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
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
        time_buttons = [[t] for t in times]
        reply_markup = ReplyKeyboardMarkup(time_buttons, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"📅 Sana tanlandi: {selected_date}\n\nEndi vaqtni tanlang:", reply_markup=reply_markup)

# Vaqt tanlash
async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_time = update.message.text
    if selected_time in times:
        selected_service = context.user_data.get("selected_service", "Noma'lum")
        selected_date = context.user_data.get("selected_date", "Noma'lum")
        await update.message.reply_text(
            f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {selected_service}\n📅 Sana: {selected_date}\n🕒 Vaqt: {selected_time}\n\nTez orada siz bilan bog‘lanamiz!"
        )

# 📋 Xizmat turlari tugmasi bosilganda
async def handle_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)

# /cabinet komandasi
async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking_history = "Hozircha hech qanday bandlov mavjud emas."
    cashback_amount = "0 so'm"
    referral_count = 0
    text = (
        f"👤 Shaxsiy kabinet:\n\n"
        f"📅 Bandlovlar tarixi:\n{booking_history}\n\n"
        f"💰 Keshbek: {cashback_amount}\n"
        f"👥 Taklif qilgan do‘stlaringiz: {referral_count} ta"
    )
    await update.message.reply_text(text)

# === BOTNI ISHGA TUSHIRISH ===
if __name__ == '__main__':
    app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("cabinet", cabinet))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(services)})$"), choose_service))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(get_next_dates())})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(times)})$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Xizmat turlari$"), handle_services_button))

    app.run_polling()






