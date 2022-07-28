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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("1x1", callback_data="800/800"),
            InlineKeyboardButton("2x3", callback_data="744/1133"),
        ],
        [InlineKeyboardButton("4x3", callback_data="1080/810")],
        [InlineKeyboardButton("Wallpaper", callback_data="1170/2532")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose aspect ratio:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def random_img():
        n = random.randint(1, 10000000)
        url = f'https://picsum.photos/{query.data}?random={str(n)}'
        return url
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=random_img())


async def gif(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contents = requests.get(
        'https://api.giphy.com/v1/gifs/random?api_key=HEpBPk8ptZEhZTuiLsyZutBJxDMZDrst&tag=&rating=pg-13').json()
    data = contents['data']
    url = data['bitly_url']
    await update.message.reply_text(url)


if __name__ == '__main__':
    application = Application.builder().token("5360990261:AAGMygeJJbzHeRRkDfc9KIcdDDOF-vF_66s").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gif", gif))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()