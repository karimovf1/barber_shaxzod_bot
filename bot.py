from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom, xush kelibsiz!\n"
        "Bu — Barber Shaxzod bot.\n\n"
        "✂️ Soch oldirishga yozilishingiz,\n"
        "💰 Keshbek olishingiz,\n"
        "👥 Do‘stlarni taklif qilishingiz mumkin.\n\n"
        "Boshlash uchun menyudan tanlang."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
