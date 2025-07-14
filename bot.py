from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus"

# /start komandasi uchun tugmali interfeys
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✂️ Xizmatlar", callback_data="xizmat")],
        [InlineKeyboardButton("👤 Kabinet", callback_data="kabinet")],
        [InlineKeyboardButton("📅 Bandlovni bekor qilish", callback_data="bekor")],
        [InlineKeyboardButton("📍 Lokatsiya", callback_data="location")],
        [InlineKeyboardButton("📸 Instagram", callback_data="instagram")],
        [InlineKeyboardButton("📲 Telegram", callback_data="telegram")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Asosiy menyu:", reply_markup=reply_markup)

# Callback tugmalarni qayta ishlash
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "xizmat":
        await query.edit_message_text("📋 Xizmatlar ro'yxati: (bu yerga xizmatlar qo‘shiladi)")
    elif data == "kabinet":
        await query.edit_message_text("👤 Shaxsiy kabinet: (keyinchalik bu yerga ma’lumot chiqadi)")
    elif data == "bekor":
        await query.edit_message_text("❌ Bandlovni bekor qilish: (bandlov bo‘lsa bekor qilinadi)")
    elif data == "location":
        await query.edit_message_text("📍 Lokatsiya: https://maps.app.goo.gl/rSNBiU5V4uxBsCgB9")
    elif data == "instagram":
        await query.edit_message_text("📸 Instagram: https://www.instagram.com/barber_shaxzod")
    elif data == "telegram":
        await query.edit_message_text("📲 Telegram: https://t.me/barbershaxzod")
    elif data == "help":
        await query.edit_message_text("ℹ️ Yordam uchun admin bilan bog‘laning: @barber_shaxzod")
    else:
        await query.edit_message_text("❓ Noma’lum tanlov.")

# Asosiy ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot ishga tushdi...")
    app.run_polling()
