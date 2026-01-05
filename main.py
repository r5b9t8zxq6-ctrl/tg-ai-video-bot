import os
import replicate
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ===== ENV =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # https://your-app.onrender.com

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# ===== TELEGRAM APP =====
bot = Bot(token=TELEGRAM_TOKEN)
app = Application.builder().token(TELEGRAM_TOKEN).build()

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 Напиши текст — я сгенерирую ИИ-видео.\n\nПример:\nМотивационное видео про дисциплину"
    )

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("⏳ Генерирую видео, подожди 1–2 минуты...")

    output = replicate.run(
        "stability-ai/stable-video-diffusion",
        input={
            "prompt": prompt,
            "num_frames": 14
        }
    )

    video_url = output[0]
    await update.message.reply_video(video=video_url)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))

# ===== FLASK =====
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot is alive", 200

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    app.update_queue.put_nowait(update)
    return "ok", 200

# ===== START =====
if __name__ == "__main__":
    import asyncio

    async def main():
        await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        await app.initialize()
        await app.start()

    asyncio.run(main())
    flask_app.run(host="0.0.0.0", port=10000)
