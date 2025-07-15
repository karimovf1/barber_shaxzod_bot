from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus"

# START komandasi — foydalanuvchi birinchi marta botga kirganda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✂️ Xizmatlar", callback_data="xizmat")],
        [InlineKeyboardButton("👤 Shaxsiy kabinet", callback_data="kabinet")],
        [InlineKeyboardButton("📅 Bandlovni bekor qilish", callback_data="bekor")],
        [InlineKeyboardButton("📍 Lokatsiya", callback_data="location")],
        [InlineKeyboardButton("📸 Instagram", callback_data="instagram")],
        [InlineKeyboardButton("📲 Telegram", callback_data="telegram")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    await update.message.reply_text(
        "Assalomu alaykum! Quyidagilardan birini tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# INLINE TUGMALARGA JAVOB
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "xizmat":
        await query.edit_message_text("📋 Xizmatlar ro'yxati (bu joyga keyinchalik xizmatlar qo‘shiladi).")
    elif data == "kabinet":
        await query.edit_message_text("👤 Bu yerda shaxsiy kabinet bo'ladi.")
    elif data == "bekor":
        await query.edit_message_text("❌ Bandlov bekor qilish bu yerda ishlaydi.")
    elif data == "location":
        await query.edit_message_text("📍 Lokatsiyamiz: Bunyodkor shoh ko‘chasi 8Д, Toshkent.")
    elif data == "instagram":
        await query.edit_message_text("📸 Instagram: https://www.instagram.com/barber_shaxzod")
    elif data == "telegram":
        await query.edit_message_text("📲 Telegram: https://t.me/barbershaxzod")
    elif data == "help":
        await query.edit_message_text("ℹ️ Yordam uchun admin: @barber_shaxzod")
    else:
        await query.edit_message_text("❓ Noma’lum tanlov.")

# ASOSIY
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
