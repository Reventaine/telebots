import openai
import logging
import time
from config import openaiToken as openaiToken
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram.error import TimedOut

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

IMAGE, CHAT = range(2)

openai.api_key = openaiToken


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("/text to use text neuralink or /image to generate images")
    return ConversationHandler.END


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter a request or /image to generate images")
    return CHAT


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text

    msg = await update.message.reply_text(f"Building an answer...")
    msg

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    await msg.edit_text(text=response['choices'][0]['text'])
    time.sleep(1)
    return await start(update, context)


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter a request for image or /start")
    return IMAGE


async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = update.message.text

    await update.message.reply_text(f"Building an images...")

    response = openai.Image.create(
        prompt=prompt,
        n=3,
        size="1024x1024"
    )

    for i in range(3):
        await update.message.reply_photo(photo=response['data'][i]['url'])
        time.sleep(1)
    return await start(update, context)


if __name__ == '__main__':
    application = Application.builder().token("5560967942:AAGgMQFSrXJBOwZCvV01g_3uhad2pjGlMoI").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("text", text),
            CommandHandler('image', image),
        ],
        states={
            CHAT: [
                MessageHandler(filters.TEXT & (~ filters.COMMAND) & (~ filters.Regex('Image')), chat)
            ],
            IMAGE: [
                MessageHandler(filters.Regex("^(Image)$"), image),
                MessageHandler(filters.TEXT & (~ filters.COMMAND) & (~ filters.Regex('Image')), get_image)
            ],
        },
        fallbacks=[CommandHandler("text", text), CommandHandler("image", image)], allow_reentry=True,
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.run_polling()
