from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# /start komandasi — inline menyu chiqaradi
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

    await update.message.reply_text(
        "Assalomu alaykum, <b>Barber Shaxzod</b> botiga xush kelibsiz!\n\nQuyidagilardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# Inline tugmalar bosilganda ishlovchi funksiya
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "xizmat":
        await query.edit_message_text("📋 Xizmatlar ro'yxati (bu yerga xizmatlar qo‘shiladi)")
    elif data == "kabinet":
        await query.edit_message_text("👤 Shaxsiy kabinet (keyinchalik ma’lumotlar bilan to‘ldiriladi)")
    elif data == "bekor":
        await query.edit_message_text("❌ Bandlov bekor qilish (hali ishlanmoqda)")
    elif data == "location":
        await query.edit_message_location(latitude=41.306167, longitude=69.236028)
    elif data == "instagram":
        await query.edit_message_text("📸 Instagram sahifamiz:\nhttps://www.instagram.com/barber_shaxzod")
    elif data == "telegram":
        await query.edit_message_text("📲 Telegram sahifamiz:\nhttps://t.me/barbershaxzod")
    elif data == "help":
        await query.edit_message_text("ℹ️ Yordam uchun admin: @barber_shaxzod")
    else:
        await query.edit_message_text("❓ Noma’lum tanlov.")

# Botni ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token("8112474957:AAHAUjJwLGAku4RJZUKtlgQnB92EEsaIZus").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
