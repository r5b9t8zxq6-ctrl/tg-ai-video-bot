import os
import replicate
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== ENV =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 Напиши описание сцены — я сгенерирую ИИ-видео"
    )

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("⏳ Генерирую видео, подожди...")

    try:
        # 1️⃣ Генерация изображения
        image = replicate.run(
            "stability-ai/sdxl",
            input={
                "prompt": prompt,
                "width": 1024,
                "height": 576
            }
        )[0]

        # 2️⃣ Видео из изображения
        video = replicate.run(
            "stability-ai/stable-video-diffusion-img2vid",
            input={
                "input_image": image,
                "motion_bucket_id": 127,
                "fps": 6
            }
        )[0]

        await update.message.reply_video(video=video)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка генерации:\n{e}")

# ===== APP =====
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))

    print("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
