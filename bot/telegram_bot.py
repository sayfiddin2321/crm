import sys
import os

# Django sozlash
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_project.settings")

import django
django.setup()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from asgiref.sync import sync_to_async
from accounts.models import CustomUser
from django.contrib.auth import authenticate

# Bot token
TOKEN = "YOUR_REAL_BOT_TOKEN"


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    user = await sync_to_async(CustomUser.objects.filter(username=username).first)()
    if user:
        user.telegram_chat_id = chat_id
        await sync_to_async(user.save)()
        await update.message.reply_text(
            f"Assalomu alaykum, {update.effective_user.first_name}! Telegram ID saqlandi."
        )
    else:
        await update.message.reply_text(
            "Siz bizning tizimda ro‘yxatdan o‘tmagansiz."
        )


# /students
async def students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = await sync_to_async(
        lambda: list(CustomUser.objects.filter(role="student"))
    )()
    if not students:
        await update.message.reply_text("📌 Hozircha o‘quvchilar yo‘q.")
    else:
        text = "📋 *O‘quvchilar ro‘yxati:*\n\n"
        for s in students:
            text += f"• @{s.username} {s.first_name} {s.last_name} ({s.phone})\n"
        await update.message.reply_text(text, parse_mode="Markdown")


# /teachers
async def teachers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teachers = await sync_to_async(
        lambda: list(CustomUser.objects.filter(role="teacher"))
    )()
    if not teachers:
        await update.message.reply_text("📌 Hozircha o‘qituvchilar yo‘q.")
    else:
        text = "👨‍🏫 *O‘qituvchilar ro‘yxati:*\n\n"
        for t in teachers:
            text += f"• @{t.username} {t.first_name} {t.last_name} ({t.phone})\n"
        await update.message.reply_text(text, parse_mode="Markdown")


# /tolov - superadmin uchun
async def tolov(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    user = await sync_to_async(CustomUser.objects.filter(username=username).first)()

    if not user or user.role != "superadmin":
        await update.message.reply_text("⛔ Bu buyruq faqat superadmin uchun.")
        return

    students = await sync_to_async(lambda: list(CustomUser.objects.filter(role="student")))()
    if not students:
        await update.message.reply_text("Hozircha o‘quvchilar yo‘q, eslatma yuborilmadi.")
        return

    eslatma = (
        "📢 Hurmatli talabalar!\n\n"
        "✅ To‘lov muddatiga diqqat qiling.\n"
        "🔹 To‘lov summasi: 500 000 so‘m\n"
        "🔹 Oxirgi kun: 5-iyul 2025\n\n"
        "Iltimos, to‘lovni vaqtida amalga oshiring."
    )

    for student in students:
        if student.telegram_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=student.telegram_chat_id,
                    text=f"Salom, {student.first_name}!\n\n{eslatma}"
                )
            except Exception as e:
                print(f"{student.username} ga yuborishda xatolik: {e}")
        else:
            print(f"{student.username} da chat_id yo‘q, yuborilmadi.")

    await update.message.reply_text("✅ To‘lov eslatmasi jo‘natildi.")


# /send - superadmin uchun
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    user = await sync_to_async(CustomUser.objects.filter(username=username).first)()

    if not user or user.role != "superadmin":
        await update.message.reply_text("⛔ Bu buyruq faqat superadmin uchun.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Foydalanish: /send @username xabar_matni")
        return

    target_username = args[0].lstrip("@")
    message_text = " ".join(args[1:])

    target_user = await sync_to_async(CustomUser.objects.filter(username=target_username).first)()
    if target_user and target_user.telegram_chat_id:
        try:
            await context.bot.send_message(
                chat_id=target_user.telegram_chat_id,
                text=message_text
            )
            await update.message.reply_text(f"✅ @{target_username} ga yuborildi.")
        except Exception as e:
            await update.message.reply_text(f"Xabar yuborishda xatolik: {e}")
    else:
        await update.message.reply_text("Bunday foydalanuvchi topilmadi yoki chat_id yo‘q.")


# /login
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Foydalanish: /login username parol")
        return

    username = args[0]
    password = " ".join(args[1:])
    chat_id = update.effective_chat.id

    user = await sync_to_async(authenticate)(username=username, password=password)

    if user is not None:
        user.telegram_chat_id = chat_id
        await sync_to_async(user.save)()
        await update.message.reply_text(
            f"✅ Salom, {user.first_name}! Telegram hisobingiz bog‘landi."
        )
    else:
        await update.message.reply_text("❌ Login yoki parol noto‘g‘ri.")


# Botni ishga tushirish
app = ApplicationBuilder().token("8108879315:AAFFfbqx1KwSOqGu19YUPnR3hyUHtdv4Qc0").build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("students", students))
app.add_handler(CommandHandler("teachers", teachers))
app.add_handler(CommandHandler("tolov", tolov))
app.add_handler(CommandHandler("send", send))
app.add_handler(CommandHandler("login", login))

if __name__ == "__main__":
    app.run_polling()
