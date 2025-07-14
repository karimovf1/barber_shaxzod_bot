from telegram.ext import CallbackQueryHandler

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "xizmat":
        await query.edit_message_text("📋 Xizmatlar ro'yxati: (keyinchalik bu yerga xizmatlarni chiqaramiz)")
    elif data == "kabinet":
        await shaxsiy_kabinet(update, context)  # Agar bu funksiya bor bo‘lsa
    elif data == "bekor":
        await bekor_qilish(update, context)
    elif data == "location":
        await google_location(update, context)
    elif data == "instagram":
        await query.edit_message_text("📸 Instagram: https://www.instagram.com/barber_shaxzod")
    elif data == "telegram":
        await query.edit_message_text("📲 Telegram: https://t.me/barbershaxzod")
    elif data == "help":
        await query.edit_message_text("ℹ️ Yordam uchun admin bilan bog‘laning: @barber_shaxzod")
    else:
        await query.edit_message_text("❓ Noma’lum tanlov.")

app.add_handler(CallbackQueryHandler(button_handler))
