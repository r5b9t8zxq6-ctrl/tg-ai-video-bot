import os
import asyncio
import replicate
from flask import Flask, request

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ========= ENV =========
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # https://xxx.onrender.com/webhook

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# ========= EVENT LOOP =========
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ========= TELEGRAM =========
application = Application.builder().token(TELEGRAM_TOKEN).build()

# ========= HANDLERS =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 Напиши описание сцены — я сгенерирую ИИ-видео"
    )

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("⏳ Генерирую видео, подожди...")

    try:
        image = replicate.run(
            "stability-ai/stable-diffusion",
            input={"prompt": prompt}
        )[0]

        video = replicate.run(
            "stability-ai/stable-video-diffusion",
            input={"input_image": image}
        )[0]

        await update.message.reply_video(video=video)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

application.add_handler(CommandHandler("start", start))
application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video)
)

# ========= FLASK =========
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def health():
    return "OK", 200

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    asyncio.run_coroutine_threadsafe(
        application.process_update(update),
        loop
    )
    return "ok", 200

# ========= STARTUP =========
def main():
    async def setup():
        await application.initialize()
        await application.bot.set_webhook(WEBHOOK_URL)

    loop.run_until_complete(setup())

    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    main()
