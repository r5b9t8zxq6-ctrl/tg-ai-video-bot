import os
import asyncio
import replicate
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== ENV =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# ===== TELEGRAM =====
bot = Bot(token=TELEGRAM_TOKEN)
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 Напиши текст — я сгенерирую ИИ-видео"
    )

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("⏳ Генерирую видео, подожди...")

    output = replicate.run(
        "stability-ai/stable-video-diffusion",
        input={
            "prompt": prompt,
            "num_frames": 14
        }
    )

    await update.message.reply_video(video=output[0])

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))

# ===== FLASK =====
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def health():
    return "Bot is alive", 200

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    tg_app.update_queue.put_nowait(update)
    return "ok", 200

# ===== STARTUP =====
async def telegram_startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    await tg_app.initialize()
    await tg_app.start()

def run():
    loop = asyncio.get_event_loop()
    loop.create_task(telegram_startup())
    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    run()
