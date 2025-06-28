from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta

# Xizmatlar ro'yxati
services = [
    "Soch olish",
    "Soqol olish",
    "Soqol togirlash",
    "Okantovka qilish",
    "Ukladka qlish",
    "Soch boyash",
    "Soqol boyash",
    "Yuzga maska qlish",
    "Yuz chiskasi",
    "Kuyov soch"
]

# Sanalarni olish funksiyasi
def get_next_dates(num_days=7):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

# Vaqt oralig'larini olish funksiyasi
def get_time_slots(start_hour=10, end_hour=18):
    return [f"{hour:02d}:00" for hour in range(start_hour, end_hour)]

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

# Sanani tanlash
async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
        context.user_data["selected_service"] = service

        dates = get_next_dates()
        date_buttons = [[d] for d in dates]
        date_markup = ReplyKeyboardMarkup(date_buttons, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            f"✅ Siz tanladingiz: {service}\n\nEndi xizmat uchun kunni tanlang:",
            reply_markup=date_markup
        )

# Vaqtni tanlash
async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_date = update.message.text
    context.user_data["selected_date"] = selected_date

    time_slots = get_time_slots()
    time_buttons = [[t] for t in time_slots]
    time_markup = ReplyKeyboardMarkup(time_buttons, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        f"📅 Sana tanlandi: {selected_date}\n\nEndi vaqtni tanlang:",
        reply_markup=time_markup
    )

# Bandlovni tasdiqlash
async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_time = update.message.text
    context.user_data["selected_time"] = selected_time

    service = context.user_data.get("selected_service")
    date = context.user_data.get("selected_date")
    time = context.user_data.get("selected_time")

    await update.message.reply_text(
        f"✅ Bandlov yakunlandi!\n\n📋 Xizmat: {service}\n📅 Sana: {date}\n🕒 Vaqt: {time}\n\nTez orada siz bilan bog‘lanamiz!"
    )

# 📋 Xizmat turlari tugmasi bosilganda /book funksiyasini chaqirish
tugma_nomi = "📋 Xizmat turlari"
async def handle_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)

# Botni ishga tushurish
if __name__ == '__main__':
    app = ApplicationBuilder().token("TOKENNI_BU_YERGA_QO'YING").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(services)})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d{4}-\d{2}-\d{2}$"), choose_time))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d{2}:\d{2}$"), confirm_booking))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{tugma_nomi}$"), handle_services_button))

    app.run_polling()



