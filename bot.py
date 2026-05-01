from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "7356647239:AAECWUz3o2VKBq0QZ0lfHQZiVynIxZMSSbU"

REQUIRED_CHANNELS = [
    {"id": "@kino_uz_channele", "name": "Kino UZ", "url": "https://t.me/kino_uz_channele"},
]

ADMIN_IDS = [6531073126]

video_db = {}

async def check_sub(user_id, bot):
    not_sub = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status in ["left", "kicked"]:
                not_sub.append(ch)
        except:
            not_sub.append(ch)
    return not_sub

def sub_keyboard(not_sub):
    buttons = [[InlineKeyboardButton(f"✅ {ch['name']}", url=ch["url"])] for ch in not_sub]
    buttons.append([InlineKeyboardButton("🔄 Tekshirish", callback_data="check")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    not_sub = await check_sub(user.id, context.bot)
    if not_sub:
        await update.message.reply_text(
            f"👋 Salom {user.first_name}!\n\n"
            "🎬 Filmni olish uchun avval kanalga obuna bo'ling 👇",
            reply_markup=sub_keyboard(not_sub)
        )
    else:
        await update.message.reply_text(
            f"👋 Salom {user.first_name}!\n\n"
            "🎬 Film kodini yuboring va kinoni oling!\n\n"
            "📌 Misol: <code>1234</code>",
            parse_mode="HTML"
        )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    not_sub = await check_sub(query.from_user.id, context.bot)
    if not_sub:
        await query.edit_message_text(
            "❌ Hali obuna bo'lmadingiz!\n\nObuna bo'lib qayta tekshiring:",
            reply_markup=sub_keyboard(not_sub)
        )
    else:
        await query.edit_message_text(
            "✅ Obuna tasdiqlandi!\n\n"
            "🎬 Endi film kodini yuboring!"
        )

async def add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text(
            "❗ Foydalanish:\n"
            "1. Botga video yuboring\n"
            "2. Shu videoga reply qilib yozing:\n"
            "<code>/add 1234</code>",
            parse_mode="HTML"
        )
        return
    kod = context.args[0]
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        file_id = None
        if msg.video:
            file_id = msg.video.file_id
        elif msg.document:
            file_id = msg.document.file_id
        if file_id:
            video_db[kod] = file_id
            await update.message.reply_text(
                f"✅ Film saqlandi!\n"
                f"📌 Kod: <code>{kod}</code>\n\n"
                f"Instagramga yozing:\n"
                f"'Filmni olish uchun botga <b>{kod}</b> yuboring'",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ Video topilmadi. Videoga reply qiling.")
    else:
        await update.message.reply_text(
            "❌ Avval video yuboring, keyin unga reply qilib:\n"
            "<code>/add 1234</code>",
            parse_mode="HTML"
        )

async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not video_db:
        await update.message.reply_text("📭 Hali film qo'shilmagan.\n\n/add buyrug'i bilan qo'shing.")
        return
    text = "🎬 <b>Filmlar ro'yxati:</b>\n\n"
    for k in video_db:
        text += f"• Kod: <code>{k}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def del_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("Foydalanish: /del KOD")
        return
    kod = context.args[0]
    if kod in video_db:
        del video_db[kod]
        await update.message.reply_text(f"✅ {kod} kodi o'chirildi.")
    else:
        await update.message.reply_text(f"❌ {kod} kodi topilmadi.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kod = update.message.text.strip()
    not_sub = await check_sub(user.id, context.bot)
    if not_sub:
        await update.message.reply_text(
            "⚠️ Avval kanalga obuna bo'ling!",
            reply_markup=sub_keyboard(not_sub)
        )
        return
    if kod in video_db:
        await update.message.reply_text("⏳ Yuklanmoqda...")
        try:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_db[kod],
                caption=f"🎬 Mana sizning filmingiz!\n\nKod: <code>{kod}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")
    else:
        await update.message.reply_text(
            "❌ Bunday kod topilmadi!\n"
            "Kodni to'g'ri yozdingizmi? 🤔"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_video))
    app.add_handler(CommandHandler("list", list_videos))
    app.add_handler(CommandHandler("del", del_video))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="check"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
