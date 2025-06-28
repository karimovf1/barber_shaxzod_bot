from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv

# Tokenni yuklash
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Asosiy menyu tugmalari
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        ["/book", "/cabinet"],
        ["/referal", "/cashback"],
        ["/instagram", "/location"],
        ["/help", "📋 Xizmat turlari"]
    ],
    resize_keyboard=True
)

# Xizmatlar ro‘yxati
services = [
    "Soch olish", "Soqol olish", "Soqol to‘g‘irlash", "Okantovka qilish",
    "Ukladka qilish", "Soch bo‘yash", "Soqol bo‘yash", "Yuzga maska qilish",
    "Yuz chiskasi", "Kuyov sochi"
]

# Xizmatlar tugmalari
service_markup = ReplyKeyboardMarkup(
    [[s] for s in services],
    resize_keyboard=True,
    one_time_keyboard=True
)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum, 'Barber Shaxzod' botiga xush kelibsiz!\nQuyidagilardan birini tanlang 👇",
        reply_markup=main_menu
    )

# /book komandasi
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Iltimos, qaysi xizmatni tanlang:",
        reply_markup=service_markup
    )

# Xizmat tanlanganida ishlaydi
async def service_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service in services:
        await update.message.reply_text(f"✅ Siz tanladingiz: {service}\n\nTez orada bu xizmat uchun bandlov qismi qo‘shiladi.")

# /cabinet komandasi
async def cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Shaxsiy kabinet funksiyasi hali sozlanmoqda.")

# /referal komandasi
async def referal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"🔗 Sizning referal havolangiz:\nhttps://t.me/barber_shaxzod_bot?start={user_id}")

# /cashback komandasi
async def cashback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💸 Sizda hozircha 0 so'm keshbek bor. Takliflar uchun keshbek tizimi ishlaydi.")

# /instagram komandasi
async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Instagram sahifamiz:\nhttps://www.instagram.com/barber_shaxzod")

# /location komandasi
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Manzilimiz: Toshkent shahri, Sergeli tumani, Barbershop Shaxzod")

# /help komandasi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam: Har bir tugma o‘ziga mos xizmatni bajaradi. Qo‘shimcha savollar bo‘lsa, admin: @karimovf_1")

# 📋 Xizmat turlari tugmasi
async def services_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    services_text = "💈 Xizmat turlari:\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(services)])
    await update.message.reply_text(services_text)

# Botni ishga tushurish
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

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📋 Xizmat turlari"), services_list))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, service_choice))

    app.run_polling()
