from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import asyncio
import csv
import os
import re

# Admin ID
ADMIN_ID = 123456789  # <-- bu yerga admin Telegram ID qo'yiladi

# Referrallar, cashback, bandlovlar
referrals_data = {}
cashback_data = {}
user_bookings = {}
user_cancel_limits = {}

# Xizmatlar ro'yxati
services = [
    "Soch olish – 200 000 so'm (yoshlar: 150 000 so'm)",
    "Soqol olish – 70 000 so'm",
    "Soqol to‘g‘rilash – 70 000 so'm",
    "Okantovka qilish – 50 000 so'm",
    "Ukladka qilish – 100 000+ so'm",
    "Soch bo‘yash – 70 000 so'm",
    "Soqol bo‘yash – 50 000 so'm",
    "Yuzga maska qilish – 50 000+ so'm",
    "Yuz chiskasi – 200 000 so'm",
    "Kuyov sochi – 50$"
]

escaped_services = [re.escape(s) for s in services]
service_pattern = f"^({'|'.join(escaped_services)})$"

def get_next_dates(num_days=7):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

# Vaqtlar (09:00-21:00)
times = [f"{hour:02d}:00" for hour in range(9, 22)]
booked_slots = {}

def save_booking_to_csv(user_id, service, date, time, phone=None):
    file_exists = os.path.isfile("bookings.csv")
    with open("bookings.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["user_id", "phone", "service", "date", "time", "timestamp"])
        writer.writerow([user_id, phone or "N/A", service, date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def get_main_menu():
    return ReplyKeyboardMarkup(
        [["/xizmat"], ["/shaxsiy_kabinet"], ["/bekor_qilish"], ["/admin"], ["/referal"], ["/cashback"],
         ["/instagram", "/telegram"], ["\ud83d\udccd Google manzil"], ["/help"], ["\ud83d\udccb Xizmat turlari"]],
        resize_keyboard=True
    )

def get_back_button():
    return ReplyKeyboardMarkup([["\ud83d\udd19 Orqaga / Назад"]], resize_keyboard=True, one_time_keyboard=True)

async def ask_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\ud83d\udcf1 Iltimos, telefon raqamingizni ulashing:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("\ud83d\udcf2 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True
        )
    )
    context.user_data["step"] = "get_phone"

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        context.user_data["phone"] = contact.phone_number
        await update.message.reply_text("\u2705 Telefon raqami qabul qilindi.", reply_markup=get_main_menu())
        await book(update, context)

# (qolgan funksiyalarni siz yuborgan koddan hech narsani o'zgartirmay saqladik)

# --- Shu yerga sizning qolgan barcha funksiyalaringiz kiradi (start, book, choose_service, choose_date...) ---
# --- Faqat choose_time() ichiga telefon raqamni CSV saqlovga qo‘shdik ---

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["step"] = "done"
    time = update.message.text.replace(" \u274c Band", "")
    service = context.user_data.get("selected_service")
    date = context.user_data.get("selected_date")
    user_id = update.effective_user.id

    if not service or not date:
        await update.message.reply_text("Iltimos, avval xizmat va sanani tanlang.")
        return

    busy = booked_slots.setdefault(date, {}).setdefault(service, set())
    if time in busy:
        await update.message.reply_text("\u274c Bu vaqt allaqachon band. Iltimos, boshqa vaqt tanlang.")
        return

    existing = user_bookings.get(user_id)
    if existing and not existing.get("cancelled"):
        await update.message.reply_text("\u274c Sizda mavjud bandlov bor. Avval bekor qiling yoki kuting.")
        return

    busy.add(time)
    phone = context.user_data.get("phone")
    user_bookings[user_id] = {
        "service": service, "date": date, "time": time,
        "cancelled": False, "cancel_count": existing.get("cancel_count", 0) if existing else 0,
        "last_cancel": existing.get("last_cancel") if existing else None
    }

    save_booking_to_csv(user_id, service, date, time, phone)

    booking_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    remind_time = booking_datetime - timedelta(hours=1)
    now = datetime.now()
    if remind_time > now:
        wait_seconds = (remind_time - now).total_seconds()
        asyncio.create_task(schedule_reminder(update, context, wait_seconds, booking_datetime.strftime("%H:%M")))

    await update.message.reply_text(f"\u2705 Bandlov yakunlandi!\n\n\ud83d\udccb Xizmat: {service}\n\ud83d\udcc5 Sana: {date}\n\ud83d\udd52 Vaqt: {time}", reply_markup=get_main_menu())

# --- Qo‘shimcha handler ---
app = ApplicationBuilder().token("BOT_TOKENINGIZNI_QO'YING").build()
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

# (Sizning boshqa handlerlaringiz ham shu yerga qo‘shiladi: start, book, admin va h.k.)

app.run_polling()
