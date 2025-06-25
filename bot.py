import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Tokenni yuklaymiz
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Logger sozlamalari
logging.basicConfig(level=logging.INFO)

# /start komandasi uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Barber Shaxzod botiga xush kelibsiz!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
