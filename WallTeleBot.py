import logging, random, requests, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

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
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def wallpaper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Phone", callback_data="1284/2778"),
            InlineKeyboardButton("Pad", callback_data="2048/2732"),
        ],
        [InlineKeyboardButton("Desktop", callback_data="4096/2160")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose device:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def random_img():
        n = random.randint(1, 10000000)
        url = f'https://picsum.photos/{query.data}?random={str(n)}'
        return url
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='This is your wallpaper:')
    await query.message.reply_photo(random_img())


if __name__ == '__main__':
    application = Application.builder().token("*TOKEN*").build()
    application.add_handler(CommandHandler("Wallpaper", wallpaper))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()
