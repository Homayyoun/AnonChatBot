from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import uuid
from datetime import datetime
import asyncio

# توکن ربات
TOKEN = "7897612319:AAEaCnJcS_NUMHv-yCxe1jZY4RylFe-20r0"  # توکنت رو بذار

# دیکشنری‌ها
users = {}
chat_map = {}
pending_reply = {}
pending_chat = {}
message_counts = {}
active_chat = {}
first_message_sent = set()

# منوی اصلی
main_menu = ReplyKeyboardMarkup([
    [KeyboardButton("/link - ساخت لینک"), KeyboardButton("/list - لیست افراد")],
    [KeyboardButton("/end - بستن گفتگو"), KeyboardButton("/close - قطع کامل")]
], resize_keyboard=True)

async def generate_link(update, context):
    chat_id = update.message.chat_id
    unique_id = str(uuid.uuid4())
    users[unique_id] = chat_id
    link = f"https://t.me/ananymouChatbot2_bot?start={unique_id}"
    print(f"لینک ساخته شد: {link}, users: {users}")
    await update.message.reply_text(
        "🎉 لینک چت ناشناس شما آماده‌ست!\n"
        f"🔗 {link}\n"
        "این لینک رو به هرکی بدی، می‌تونه بدون اینکه اسمش رو بفهمی باهات چت کنه. بفرست و منتظر پیامش باش! 😎",
        reply_markup=main_menu
    )

async def start(update, context):
    chat_id = update.message.chat_id
    print(f"درخواست از chat_id: {chat_id}, پیام: {update.message.text}")
    args = context.args
    if args:
        unique_id = args[0]
        print(f"کد یکتا: {unique_id}, users: {users}")
        if unique_id in users:
            chat_map[chat_id] = users[unique_id]
            message_counts[chat_id] = message_counts.get(chat_id, 0)
            print(f"chat_map به‌روزرسانی شد: {chat_map}")
            await update.message.reply_text(
                "🌙 به دنیای چت ناشناس خوش اومدی!\n"
                "اینجا می‌تونی آزادانه پیام بفرستی، بدون اینکه کسی بفهمه کی هستی.\n"
                "✍️ یه پیام متنی، صوتی یا رسانه بفرست و چت رو شروع کن!\n"
                "📸 عکس یا ویدئوها به خاطر حریم خصوصی قابل ذخیره نیست و بعد از ۱۰ ثانیه برای تو پاک می‌شه."
            )
            return
        else:
            await update.message.reply_text(
                "❌ اوپس! این لینک درست نیست.\n"
                "لطفاً از یه لینک معتبر استفاده کن یا از سازنده لینک بخواه یه لینک جدید بفرسته."
            )
            return
    await update.message.reply_text(
        "👋 سلام به ربات چت ناشناس!\n"
        "من اینجام که بهت کمک کنم با بقیه چت کنی، بدون اینکه هویتت رو بدونن.\n"
        "🔗 از /list برای انتخاب کاربر و شروع چت استفاده کن!\n"
        "💡 برای بستن موقت از /end و برای قطع کامل از /close استفاده کن.",
        reply_markup=main_menu
    )

async def list_users(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی! اول با دکمه 'ساخت لینک' یه لینک بساز.")
        return
    if not chat_map:
        await update.message.reply_text("🤔 هنوز کسی از لینکت وارد نشده!")
        return
    user_list = []
    buttons = []
    for anon_id, owner_id in chat_map.items():
        if owner_id == sender_id:
            chat = await context.bot.get_chat(anon_id)
            username = chat.username or "ناشناس"
            msg_count = message_counts.get(anon_id, 0)
            user_list.append(f"👤 ID: {anon_id}, Username: @{username}, پیام‌ها: {msg_count}")
            buttons.append([
                InlineKeyboardButton(f"شروع چت با @{username}", callback_data=f"chat_{anon_id}"),
                InlineKeyboardButton(f"قطع کامل @{username}", callback_data=f"close_{anon_id}")
            ])
    user_list_text = "\n".join(user_list)
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        f"📋 لیست افراد متصل:\n{user_list_text}\n"
        "برای شروع چت از 'شروع چت با...'، برای قطع کامل از 'قطع کامل...' یا /close استفاده کن.",
        reply_markup=reply_markup
    )

async def broadcast_message(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی! اول با دکمه 'ساخت لینک' یه لینک بساز.")
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً پیامت رو بعد از /broadcast بنویس! مثلاً:\n/broadcast سلام به همه")
        return
    message = " ".join(context.args)
    if not chat_map:
        await update.message.reply_text("🤔 هنوز کسی از لینکت وارد نشده!")
        return
    for anon_id, owner_id in chat_map.items():
        if owner_id == sender_id:
            await context.bot.send_message(
                chat_id=anon_id,
                text=f"📣 پیام از طرف مقابل برای همه:\n💬 {message}"
            )
    await update.message.reply_text(
        "✅ پیامت به همه کاربران متصل ارسال شد!",
        reply_markup=main_menu
    )

async def invite_user(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی! اول با دکمه 'ساخت لینک' یه لینک بساز.")
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً آیدی کاربری که می‌خوای دعوت کنی رو بنویس! مثلاً:\n/invite 123456789")
        return
    try:
        anon_id = int(context.args[0])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            new_unique_id = str(uuid.uuid4())
            users[new_unique_id] = sender_id
            new_link = f"https://t.me/ananymouChatbot2_bot?start={new_unique_id}"
            await context.bot.send_message(
                chat_id=anon_id,
                text=f"📩 دعوت جدید برای چت!\n"
                     f"لطفاً از این لینک جدید استفاده کن: {new_link}"
            )
            await update.message.reply_text(
                f"✅ لینک جدید برای کاربر (ID: {anon_id}) ارسال شد:\n{new_link}",
                reply_markup=main_menu
            )
        else:
            await update.message.reply_text("❌ این کاربر متصل به تو نیست یا وجود نداره!")
    except ValueError:
        await update.message.reply_text("❌ آیدی باید عدد باشه! از /list آیدی رو ببین.")

async def end_chat(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی!")
        return
    if sender_id in active_chat:
        anon_id = active_chat[sender_id]
        del active_chat[sender_id]
        await update.message.reply_text(
            f"✅ چت با کاربر (ID: {anon_id}) بسته شد. برای چت با نفر بعدی از /list استفاده کن.",
            reply_markup=main_menu
        )
    else:
        await update.message.reply_text("❌ الان با کسی چت نمی‌کنی! از /list یه نفر رو انتخاب کن.")

async def close_chat(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی!")
        return
    if not context.args and sender_id in active_chat:
        anon_id = active_chat[sender_id]
        del chat_map[anon_id]
        del active_chat[sender_id]
        await update.message.reply_text(
            f"✅ چت با کاربر (ID: {anon_id}) کلاً قطع شد.",
            reply_markup=main_menu
        )
        await context.bot.send_message(
            chat_id=anon_id,
            text="📢 چت شما توسط سازنده لینک کلاً بسته شد."
        )
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً آیدی کاربری که می‌خوای قطع کنی رو بنویس! مثلاً: /close 123456789")
        return
    try:
        anon_id = int(context.args[0])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            del chat_map[anon_id]
            if sender_id in active_chat and active_chat[sender_id] == anon_id:
                del active_chat[sender_id]
            await update.message.reply_text(
                f"✅ چت با کاربر (ID: {anon_id}) کلاً قطع شد.",
                reply_markup=main_menu
            )
            await context.bot.send_message(
                chat_id=anon_id,
                text="📢 چت شما توسط سازنده لینک کلاً بسته شد."
            )
        else:
            await update.message.reply_text("❌ این کاربر متصل به تو نیست یا وجود نداره!")
    except ValueError:
        await update.message.reply_text("❌ آیدی باید عدد باشه! از /list آیدی رو ببین.")

async def handle_message(update, context):
    sender_id = update.message.chat_id
    sender_username = update.message.from_user.username or "ناشناس"
    print(f"پیام از {sender_id}, users: {users}, chat_map: {chat_map}, active_chat: {active_chat}")

    if sender_id in chat_map:
        owner_id = chat_map[sender_id]
        message_counts[sender_id] = message_counts.get(sender_id, 0) + 1
        if owner_id in active_chat and active_chat[owner_id] == sender_id:
            keyboard = []  # هیچ دکمه‌ای نشون نده
        else:
            keyboard = [
                [InlineKeyboardButton("شروع چت", callback_data=f"chat_{sender_id}"),
                 InlineKeyboardButton("قطع کامل", callback_data=f"close_{sender_id}")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message.text:
            message = update.message.text
            await context.bot.send_message(
                chat_id=owner_id,
                text=f"📩 پیام از کاربر ناشناس (ID: {sender_id}, Username: @{sender_username}):\n💬 {message}",
                reply_markup=reply_markup
            )
            if sender_id not in first_message_sent:
                await update.message.reply_text(
                    "✅ پیامت با موفقیت رفت!\n"
                    "هویتت کاملاً مخفیه، منتظر جوابش باش! 😉"
                )
                first_message_sent.add(sender_id)
        elif update.message.voice:
            caption = update.message.caption or "پیام صوتی"
            await context.bot.send_message(
                chat_id=owner_id,
                text=f"📩 پیام صوتی از کاربر ناشناس (ID: {sender_id}, Username: @{sender_username}):\n📝 {caption}",
                reply_markup=reply_markup
            )
            await context.bot.send_voice(
                chat_id=owner_id,
                voice=update.message.voice.file_id,
                caption=caption
            )
            if sender_id not in first_message_sent:
                await update.message.reply_text(
                    "✅ پیام صوتیت با موفقیت رفت!\n"
                    "هویتت کاملاً مخفیه، منتظر جوابش باش! 😉"
                )
                first_message_sent.add(sender_id)
        elif update.message.photo or update.message.video:
            media_type = "عکس" if update.message.photo else "ویدئو"
            caption = update.message.caption or ""
            msg_for_owner = await context.bot.send_message(
                chat_id=owner_id,
                text=f"📩 {media_type} از کاربر ناشناس (ID: {sender_id}, Username: @{sender_username}):\n📝 {caption}",
                reply_markup=reply_markup
            )
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=owner_id,
                    photo=update.message.photo[-1].file_id,
                    caption=caption
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=owner_id,
                    video=update.message.video.file_id,
                    caption=caption
                )
            if sender_id not in first_message_sent:
                msg_for_sender = await update.message.reply_text(
                    f"✅ {media_type} شما ارسال شد!\n"
                    f"⚠️ به خاطر حریم خصوصی، این {media_type} قابل ذخیره نیست و بعد از ۱۰ ثانیه برای هر دو طرف پاک می‌شه.",
                    protect_content=True
                )
                await asyncio.sleep(10)
                await context.bot.delete_message(chat_id=sender_id, message_id=update.message.message_id)
                await context.bot.delete_message(chat_id=sender_id, message_id=msg_for_sender.message_id)
                await context.bot.send_message(
                    chat_id=sender_id,
                    text=f"📢 {media_type} یا فیلمی که فرستادی به صورت دوطرفه پاک شد و کسی نمی‌تونه اون رو ذخیره کنه."
                )
                first_message_sent.add(sender_id)
            else:
                await asyncio.sleep(10)
                await context.bot.delete_message(chat_id=sender_id, message_id=update.message.message_id)
        return

    for unique_id, owner_id in users.items():
        if sender_id == owner_id:
            if sender_id in active_chat:
                anon_id = active_chat[sender_id]
                print(f"ارسال پیام به {anon_id}")
                if update.message.text:
                    await context.bot.send_message(
                        chat_id=anon_id,
                        text=f"📩 پیام از طرف مقابل:\n💬 {update.message.text}"
                    )
                elif update.message.voice:
                    caption = update.message.caption or "پیام صوتی"
                    await context.bot.send_message(
                        chat_id=anon_id,
                        text=f"📩 پیام صوتی از طرف مقابل:\n📝 {caption}"
                    )
                    await context.bot.send_voice(
                        chat_id=anon_id,
                        voice=update.message.voice.file_id,
                        caption=caption
                    )
                await update.message.reply_text("", reply_markup=main_menu)  # فقط منو اصلی
                return
            await update.message.reply_text(
                "📬 برای شروع چت، از /list یه نفر رو انتخاب کن!\n"
                "📣 برای پیام به همه از /broadcast استفاده کن.",
                reply_markup=main_menu
            )
            return

async def handle_callback(update, context):
    query = update.callback_query
    sender_id = query.message.chat_id
    data = query.data

    if data.startswith("chat_"):
        anon_id = int(data.split("_")[1])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            active_chat[sender_id] = anon_id
            chat = await context.bot.get_chat(anon_id)
            username = chat.username or "ناشناس"
            await query.answer(f"چت با @{username} شروع شد!")
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ چت با @{username} شروع شد! پیامت رو بفرست."
            )
        else:
            await query.answer("کاربر پیدا نشد!")
    elif data.startswith("close_"):
        anon_id = int(data.split("_")[1])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            del chat_map[anon_id]
            if sender_id in active_chat and active_chat[sender_id] == anon_id:
                del active_chat[sender_id]
            await query.answer("چت کلاً قطع شد!")
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ چت با کاربر (ID: {anon_id}) کلاً قطع شد!"
            )
            await context.bot.send_message(
                chat_id=anon_id,
                text="📢 چت شما توسط سازنده لینک کلاً بسته شد."
            )
        else:
            await query.answer("کاربر پیدا نشد!")
    elif data.startswith("invite_"):
        anon_id = int(data.split("_")[1])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            new_unique_id = str(uuid.uuid4())
            users[new_unique_id] = sender_id
            new_link = f"https://t.me/ananymouChatbot2_bot?start={new_unique_id}"
            await context.bot.send_message(
                chat_id=anon_id,
                text=f"📩 دعوت جدید برای چت!\n"
                     f"لطفاً از این لینک جدید استفاده کن: {new_link}"
            )
            await query.answer("لینک جدید ارسال شد!")
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ لینک جدید برای کاربر (ID: {anon_id}) ارسال شد:\n{new_link}"
            )
        else:
            await query.answer("کاربر پیدا نشد!")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        print("ربات شروع شد!")
    except Exception as e:
        print(f"خطا توی شروع: {e}")
        return

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", generate_link))
    application.add_handler(CommandHandler("list", list_users))
    application.add_handler(CommandHandler("broadcast", broadcast_message))
    application.add_handler(CommandHandler("invite", invite_user))
    application.add_handler(CommandHandler("end", end_chat))
    application.add_handler(CommandHandler("close", close_chat))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
=======
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import uuid
from datetime import datetime
import asyncio

# توکن ربات
TOKEN = "7897612319:AAEaCnJcS_NUMHv-yCxe1jZY4RylFe-20r0"

# دیکشنری‌ها
users = {}
chat_map = {}
pending_reply = {}
pending_chat = {}
message_counts = {}
active_chat = {}
first_message_sent = set()

# منوی اصلی
main_menu = ReplyKeyboardMarkup([
    [KeyboardButton("/link - ساخت لینک"), KeyboardButton("/list - لیست افراد")],
    [KeyboardButton("/end - بستن گفتگو"), KeyboardButton("/close - قطع کامل")]
], resize_keyboard=True)

async def generate_link(update, context):
    chat_id = update.message.chat_id
    unique_id = str(uuid.uuid4())
    users[unique_id] = chat_id
    link = f"https://t.me/ananymouChatbot2_bot?start={unique_id}"
    print(f"لینک ساخته شد: {link}, users: {users}")
    await update.message.reply_text(
        "🎉 لینک چت ناشناس شما آماده‌ست!\n"
        f"🔗 {link}\n"
        "این لینک رو به هرکی بدی، می‌تونه بدون اینکه اسمش رو بفهمی باهات چت کنه. بفرست و منتظر پیامش باش! 😎",
        reply_markup=main_menu
    )

async def start(update, context):
    chat_id = update.message.chat_id
    print(f"درخواست از chat_id: {chat_id}, پیام: {update.message.text}")
    args = context.args
    if args:
        unique_id = args[0]
        print(f"کد یکتا: {unique_id}, users: {users}")
        if unique_id in users:
            chat_map[chat_id] = users[unique_id]
            message_counts[chat_id] = message_counts.get(chat_id, 0)
            print(f"chat_map به‌روزرسانی شد: {chat_map}")
            await update.message.reply_text(
                "🌙 به دنیای چت ناشناس خوش اومدی!\n"
                "اینجا می‌تونی آزادانه پیام بفرستی، بدون اینکه کسی بفهمه کی هستی.\n"
                "✍️ یه پیام متنی، صوتی یا رسانه بفرست و چت رو شروع کن!\n"
                "📸 عکس یا ویدئوها به خاطر حریم خصوصی قابل ذخیره نیست و بعد از ۱۰ ثانیه برای تو پاک می‌شه."
            )
            return
        else:
            await update.message.reply_text(
                "❌ اوپس! این لینک درست نیست.\n"
                "لطفاً از یه لینک معتبر استفاده کن یا از سازنده لینک بخواه یه لینک جدید بفرسته."
            )
            return
    await update.message.reply_text(
        "👋 سلام به ربات چت ناشناس!\n"
        "من اینجام که بهت کمک کنم با بقیه چت کنی، بدون اینکه هویتت رو بدونن.\n"
        "🔗 از /list برای انتخاب کاربر و شروع چت استفاده کن!\n"
        "💡 برای بستن موقت از /end و برای قطع کامل از /close استفاده کن.",
        reply_markup=main_menu
    )

async def list_users(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی! اول با دکمه 'ساخت لینک' یه لینک بساز.")
        return
    if not chat_map:
        await update.message.reply_text("🤔 هنوز کسی از لینکت وارد نشده!")
        return
    user_list = []
    buttons = []
    for anon_id, owner_id in chat_map.items():
        if owner_id == sender_id:
            chat = await context.bot.get_chat(anon_id)
            username = chat.username or "ناشناس"
            msg_count = message_counts.get(anon_id, 0)
            user_list.append(f"👤 ID: {anon_id}, Username: @{username}, پیام‌ها: {msg_count}")
            buttons.append([
                InlineKeyboardButton(f"شروع چت با @{username}", callback_data=f"chat_{anon_id}"),
                InlineKeyboardButton(f"قطع کامل @{username}", callback_data=f"close_{anon_id}")
            ])
    user_list_text = "\n".join(user_list)
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        f"📋 لیست افراد متصل:\n{user_list_text}\n"
        "برای شروع چت از 'شروع چت با...'، برای قطع کامل از 'قطع کامل...' یا /close استفاده کن.",
        reply_markup=reply_markup
    )

async def broadcast_message(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی! اول با دکمه 'ساخت لینک' یه لینک بساز.")
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً پیامت رو بعد از /broadcast بنویس! مثلاً:\n/broadcast سلام به همه")
        return
    message = " ".join(context.args)
    if not chat_map:
        await update.message.reply_text("🤔 هنوز کسی از لینکت وارد نشده!")
        return
    for anon_id, owner_id in chat_map.items():
        if owner_id == sender_id:
            await context.bot.send_message(
                chat_id=anon_id,
                text=f"📣 پیام از طرف مقابل برای همه:\n💬 {message}"
            )
    await update.message.reply_text(
        "✅ پیامت به همه کاربران متصل ارسال شد!",
        reply_markup=main_menu
    )

async def invite_user(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی! اول با دکمه 'ساخت لینک' یه لینک بساز.")
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً آیدی کاربری که می‌خوای دعوت کنی رو بنویس! مثلاً:\n/invite 123456789")
        return
    try:
        anon_id = int(context.args[0])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            new_unique_id = str(uuid.uuid4())
            users[new_unique_id] = sender_id
            new_link = f"https://t.me/ananymouChatbot2_bot?start={new_unique_id}"
            await context.bot.send_message(
                chat_id=anon_id,
                text=f"📩 دعوت جدید برای چت!\n"
                     f"لطفاً از این لینک جدید استفاده کن: {new_link}"
            )
            await update.message.reply_text(
                f"✅ لینک جدید برای کاربر (ID: {anon_id}) ارسال شد:\n{new_link}",
                reply_markup=main_menu
            )
        else:
            await update.message.reply_text("❌ این کاربر متصل به تو نیست یا وجود نداره!")
    except ValueError:
        await update.message.reply_text("❌ آیدی باید عدد باشه! از /list آیدی رو ببین.")

async def end_chat(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی!")
        return
    if sender_id in active_chat:
        anon_id = active_chat[sender_id]
        del active_chat[sender_id]
        await update.message.reply_text(
            f"✅ چت با کاربر (ID: {anon_id}) بسته شد. برای چت با نفر بعدی از /list استفاده کن.",
            reply_markup=main_menu
        )
    else:
        await update.message.reply_text("❌ الان با کسی چت نمی‌کنی! از /list یه نفر رو انتخاب کن.")

async def close_chat(update, context):
    sender_id = update.message.chat_id
    if sender_id not in users.values():
        await update.message.reply_text("❌ تو صاحب لینک نیستی!")
        return
    if not context.args and sender_id in active_chat:
        anon_id = active_chat[sender_id]
        del chat_map[anon_id]
        del active_chat[sender_id]
        await update.message.reply_text(
            f"✅ چت با کاربر (ID: {anon_id}) کلاً قطع شد.",
            reply_markup=main_menu
        )
        await context.bot.send_message(
            chat_id=anon_id,
            text="📢 چت شما توسط سازنده لینک کلاً بسته شد."
        )
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً آیدی کاربری که می‌خوای قطع کنی رو بنویس! مثلاً: /close 123456789")
        return
    try:
        anon_id = int(context.args[0])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            del chat_map[anon_id]
            if sender_id in active_chat and active_chat[sender_id] == anon_id:
                del active_chat[sender_id]
            await update.message.reply_text(
                f"✅ چت با کاربر (ID: {anon_id}) کلاً قطع شد.",
                reply_markup=main_menu
            )
            await context.bot.send_message(
                chat_id=anon_id,
                text="📢 چت شما توسط سازنده لینک کلاً بسته شد."
            )
        else:
            await update.message.reply_text("❌ این کاربر متصل به تو نیست یا وجود نداره!")
    except ValueError:
        await update.message.reply_text("❌ آیدی باید عدد باشه! از /list آیدی رو ببین.")

async def handle_message(update, context):
    sender_id = update.message.chat_id
    sender_username = update.message.from_user.username or "ناشناس"
    print(f"پیام از {sender_id}, users: {users}, chat_map: {chat_map}, active_chat: {active_chat}")

    if sender_id in chat_map:
        owner_id = chat_map[sender_id]
        message_counts[sender_id] = message_counts.get(sender_id, 0) + 1
        if owner_id in active_chat and active_chat[owner_id] == sender_id:
            keyboard = []  # هیچ دکمه‌ای نشون نده
        else:
            keyboard = [
                [InlineKeyboardButton("شروع چت", callback_data=f"chat_{sender_id}"),
                 InlineKeyboardButton("قطع کامل", callback_data=f"close_{sender_id}")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message.text:
            message = update.message.text
            await context.bot.send_message(
                chat_id=owner_id,
                text=f"📩 پیام از کاربر ناشناس (ID: {sender_id}, Username: @{sender_username}):\n💬 {message}",
                reply_markup=reply_markup
            )
            if sender_id not in first_message_sent:
                await update.message.reply_text(
                    "✅ پیامت با موفقیت رفت!\n"
                    "هویتت کاملاً مخفیه، منتظر جوابش باش! 😉"
                )
                first_message_sent.add(sender_id)
        elif update.message.voice:
            caption = update.message.caption or "پیام صوتی"
            await context.bot.send_message(
                chat_id=owner_id,
                text=f"📩 پیام صوتی از کاربر ناشناس (ID: {sender_id}, Username: @{sender_username}):\n📝 {caption}",
                reply_markup=reply_markup
            )
            await context.bot.send_voice(
                chat_id=owner_id,
                voice=update.message.voice.file_id,
                caption=caption
            )
            if sender_id not in first_message_sent:
                await update.message.reply_text(
                    "✅ پیام صوتیت با موفقیت رفت!\n"
                    "هویتت کاملاً مخفیه، منتظر جوابش باش! 😉"
                )
                first_message_sent.add(sender_id)
        elif update.message.photo or update.message.video:
            media_type = "عکس" if update.message.photo else "ویدئو"
            caption = update.message.caption or ""
            msg_for_owner = await context.bot.send_message(
                chat_id=owner_id,
                text=f"📩 {media_type} از کاربر ناشناس (ID: {sender_id}, Username: @{sender_username}):\n📝 {caption}",
                reply_markup=reply_markup
            )
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=owner_id,
                    photo=update.message.photo[-1].file_id,
                    caption=caption
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=owner_id,
                    video=update.message.video.file_id,
                    caption=caption
                )
            if sender_id not in first_message_sent:
                msg_for_sender = await update.message.reply_text(
                    f"✅ {media_type} شما ارسال شد!\n"
                    f"⚠️ به خاطر حریم خصوصی، این {media_type} قابل ذخیره نیست و بعد از ۱۰ ثانیه برای هر دو طرف پاک می‌شه.",
                    protect_content=True
                )
                await asyncio.sleep(10)
                await context.bot.delete_message(chat_id=sender_id, message_id=update.message.message_id)
                await context.bot.delete_message(chat_id=sender_id, message_id=msg_for_sender.message_id)
                await context.bot.send_message(
                    chat_id=sender_id,
                    text=f"📢 {media_type} یا فیلمی که فرستادی به صورت دوطرفه پاک شد و کسی نمی‌تونه اون رو ذخیره کنه."
                )
                first_message_sent.add(sender_id)
            else:
                await asyncio.sleep(10)
                await context.bot.delete_message(chat_id=sender_id, message_id=update.message.message_id)
        return

    for unique_id, owner_id in users.items():
        if sender_id == owner_id:
            if sender_id in active_chat:
                anon_id = active_chat[sender_id]
                print(f"ارسال پیام به {anon_id}")
                if update.message.text:
                    await context.bot.send_message(
                        chat_id=anon_id,
                        text=f"📩 پیام از طرف مقابل:\n💬 {update.message.text}"
                    )
                elif update.message.voice:
                    caption = update.message.caption or "پیام صوتی"
                    await context.bot.send_message(
                        chat_id=anon_id,
                        text=f"📩 پیام صوتی از طرف مقابل:\n📝 {caption}"
                    )
                    await context.bot.send_voice(
                        chat_id=anon_id,
                        voice=update.message.voice.file_id,
                        caption=caption
                    )
                await update.message.reply_text("", reply_markup=main_menu)  # فقط منو اصلی
                return
            await update.message.reply_text(
                "📬 برای شروع چت، از /list یه نفر رو انتخاب کن!\n"
                "📣 برای پیام به همه از /broadcast استفاده کن.",
                reply_markup=main_menu
            )
            return

async def handle_callback(update, context):
    query = update.callback_query
    sender_id = query.message.chat_id
    data = query.data

    if data.startswith("chat_"):
        anon_id = int(data.split("_")[1])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            active_chat[sender_id] = anon_id
            chat = await context.bot.get_chat(anon_id)
            username = chat.username or "ناشناس"
            await query.answer(f"چت با @{username} شروع شد!")
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ چت با @{username} شروع شد! پیامت رو بفرست."
            )
        else:
            await query.answer("کاربر پیدا نشد!")
    elif data.startswith("close_"):
        anon_id = int(data.split("_")[1])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            del chat_map[anon_id]
            if sender_id in active_chat and active_chat[sender_id] == anon_id:
                del active_chat[sender_id]
            await query.answer("چت کلاً قطع شد!")
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ چت با کاربر (ID: {anon_id}) کلاً قطع شد!"
            )
            await context.bot.send_message(
                chat_id=anon_id,
                text="📢 چت شما توسط سازنده لینک کلاً بسته شد."
            )
        else:
            await query.answer("کاربر پیدا نشد!")
    elif data.startswith("invite_"):
        anon_id = int(data.split("_")[1])
        if anon_id in chat_map and chat_map[anon_id] == sender_id:
            new_unique_id = str(uuid.uuid4())
            users[new_unique_id] = sender_id
            new_link = f"https://t.me/ananymouChatbot2_bot?start={new_unique_id}"
            await context.bot.send_message(
                chat_id=anon_id,
                text=f"📩 دعوت جدید برای چت!\n"
                     f"لطفاً از این لینک جدید استفاده کن: {new_link}"
            )
            await query.answer("لینک جدید ارسال شد!")
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ لینک جدید برای کاربر (ID: {anon_id}) ارسال شد:\n{new_link}"
            )
        else:
            await query.answer("کاربر پیدا نشد!")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        print("ربات شروع شد!")
    except Exception as e:
        print(f"خطا توی شروع: {e}")
        return

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", generate_link))
    application.add_handler(CommandHandler("list", list_users))
    application.add_handler(CommandHandler("broadcast", broadcast_message))
    application.add_handler(CommandHandler("invite", invite_user))
    application.add_handler(CommandHandler("end", end_chat))
    application.add_handler(CommandHandler("close", close_chat))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()

if __name__ == "__main__":
    main()
>>>>>>> 2108b483acbe6b0e3a906773b198414799881c37
>>>>>>> d9807baf9fc6a6805b013597d885426c6613a1bf
