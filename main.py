import os
import replicate
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 Напиши текст — я сгенерирую ИИ-видео.\n\nПример:\nМотивационное видео про дисциплину"
    )

# Генерация видео
async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("⏳ Генерирую видео, это может занять 1–2 минуты...")

    output = replicate.run(
        "stability-ai/stable-video-diffusion",
        input={
            "prompt": prompt,
            "num_frames": 14
        }
    )

    video_url = output[0]

    await update.message.reply_video(video=video_url)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
