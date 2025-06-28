from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Tugmalar menyusi
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        ["/book", "/cabinet"],
        ["/referal", "/cashback"],
        ["/instagram", "/location"],
        ["/help", "📋 Xizmat turlari"]
    ],
    resize_keyboard=True
)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
        reply_markup=main_menu
    )


# /book komandasi
services = [
    "Soch olish", "Soqol olish", "Soqol to‘g‘irlash", "Okantovka qilish",
    "Ukladka qilish", "Soch bo‘yash", "Soqol bo‘yash", "Yuzga maska qilish",
    "Yuz chiskasi", "Kuyov sochi"
]

service_markup = ReplyKeyboardMarkup(
    [[s] for s in services],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Iltimos, qaysi xizmatni tanlang:",
        reply_markup=service_markup
    )



# Har bir tugma funksiyasi

async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Shaxsiy kabinet funksiyasi hali sozlanmoqda.")

async def referal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔗 Sizning referal havolangiz: https://t.me/barber_shaxzod_bot?start=USERID")

async def cashback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💸 Sizda hozircha 0 so'm keshbek bor. Takliflar uchun keshbek tizimi ishlaydi.")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Instagram sahifamiz: https://www.instagram.com/barber_shaxzod")

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Manzilimiz: Toshkent shahri, Sergeli tumani, Barbershop Shaxzod")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam: Har bir tugma o‘ziga mos xizmatni bajaradi. Qo‘shimcha savollar bo‘lsa, admin bilan bog‘laning: @karimovf_1")

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    services_list = (
        "💈 Xizmat turlari:\n"
        "1. Soch olish\n"
        "2. Soqol olish\n"
        "3. Soqol to‘g‘irlash\n"
        "4. Okantovka qilish\n"
        "5. Ukladka qilish\n"
        "6. Soch bo‘yash\n"
        "7. Soqol bo‘yash\n"
        "8. Yuzga maska qilish\n"
        "9. Yuz chiskasi\n"
        "10. Kuyov sochi"
    )
    await update.message.reply_text(services_list)

# Botni ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("cabinet", cabinet))
    app.add_handler(CommandHandler("referal", referal))
    app.add_handler(CommandHandler("cashback", cashback))
    app.add_handler(CommandHandler("instagram", instagram))
    app.add_handler(CommandHandler("location", location))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📋 Xizmat turlari"), services))

    app.run_polling()
