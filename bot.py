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
def get_next_dates(num_days=5):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

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

# Botni ishga tushurish
if __name__ == '__main__':
    app = ApplicationBuilder().token("TOKENNI_BU_YERGA_QO'YING").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(services)})$"), choose_date))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📋 Xizmat turlari$"), book))


    app.run_polling()

