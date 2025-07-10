from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
import logging

# Bosqichlar
PHONE, DATE, TIME, SERVICE, CONFIRM = range(5)

# Log sozlamalari
logging.basicConfig(level=logging.INFO)

# Xizmatlar ro'yxati
services = {
    "Soch olish (Umumiy)": "200 000 so'm",
    "Yosh bola": "80 000 so'm",
    "Soch olish (VIP)": "300 000 so'm",
    "Yuz tozalash (VIP)": "200 000 so'm",
}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Ro'yxatdan o'tish uchun telefon raqamingizni yuboring 👇",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
        )
    )
    return PHONE

# Telefon raqamini olish
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    context.user_data["phone"] = contact.phone_number

    await update.message.reply_text(
        "✅ Telefon raqami qabul qilindi.\nIltimos, sana kiriting (masalan: 2025-07-11):",
        reply_markup=ReplyKeyboardRemove()
    )
    return DATE

# Sana
async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    await update.message.reply_text("⏰ Endi vaqtni kiriting (masalan: 15:30):")
    return TIME

# Vaqt
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text
    markup = [[s] for s in services.keys()]
    await update.message.reply_text(
        "Qaysi xizmatni xohlaysiz?",
        reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True)
    )
    return SERVICE

# Xizmat
async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text
    if service not in services:
        await update.message.reply_text("❌ Noto‘g‘ri xizmat. Iltimos, qaytadan tanlang.")
        return SERVICE
    context.user_data["service"] = service

    msg = (
        f"📅 Sana: {context.user_data['date']}\n"
        f"⏰ Vaqt: {context.user_data['time']}\n"
        f"📞 Tel: {context.user_data['phone']}\n"
        f"💈 Xizmat: {service} - {services[service]}\n\n"
        "✅ Hammasi to‘g‘rimi?"
    )
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            [["Tasdiqlash", "Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return CONFIRM

# Tasdiqlash
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Tasdiqlash":
        await update.message.reply_text("✅ Bandlovingiz qabul qilindi. Rahmat!")
    else:
        await update.message.reply_text("❌ Bandlov bekor qilindi.")
    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Jarayon to‘xtatildi.")
    return ConversationHandler.END

# Botni ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token("BOT_TOKENINGIZNI_BU_YERGA_QO'YING").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot ishga tushdi...")
    app.run_polling()
