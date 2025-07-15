from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✂️ Xizmatlar", callback_data="xizmat")],
        [InlineKeyboardButton("👤 Shaxsiy kabinet", callback_data="kabinet")],
        [InlineKeyboardButton("📍 Lokatsiya", callback_data="location")],
        [InlineKeyboardButton("📸 Instagram", callback_data="instagram")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Assalomu alaykum! Quyidagilardan birini tanlang:",
        reply_markup=reply_markup
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

