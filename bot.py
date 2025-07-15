from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus"

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✂️ Xizmatlar", callback_data="xizmat")],
        [InlineKeyboardButton("👤 Shaxsiy kabinet", callback_data="kabinet")],
        [InlineKeyboardButton("❌ Bandlovni bekor qilish", callback_data="bekor")],
        [InlineKeyboardButton("📍 Lokatsiya", callback_data="location")],
        [InlineKeyboardButton("📸 Instagram", callback_data="instagram")],
        [InlineKeyboardButton("📲 Telegram", callback_data="telegram")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Assalomu alaykum! Botga xush kelibsiz 👋\nQuyidagi menyudan keraklisini tanlang:",
        reply_markup=reply_markup
    )

# Tugmalarni ishlovchi funksiya
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "xizmat":
        await query.edit_message_text("📋 Xizmatlar ro'yxati: (keyinchalik to‘ldiriladi)")
    elif data == "kabinet":
        await query.edit_message_text("👤 Shaxsiy kabinet: (keyinchalik to‘ldiriladi)")
    elif data == "bekor":
        await query.edit_message_text("❌ Bandlovni bekor qilish: (keyinchalik to‘ldiriladi)")
    elif data == "location":
        await query.edit_message_text("📍 Bizning lokatsiya: https://maps.google.com")
    elif data == "instagram":
        await query.edit_message_text("📸 Instagram: https://instagram.com/barber_shaxzod")
    elif data == "telegram":
        await query.edit_message_text("📲 Telegram: https://t.me/barbershaxzod")
    elif data == "help":
        await query.edit_message_text("ℹ️ Yordam uchun: @barber_shaxzod")
    else:
        await query.edit_message_text("❓ Noma’lum tanlov.")

# Ishga tushurish
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
