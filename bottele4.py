import logging, random, requests, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

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


#start

CHOOSING, BUTTON, BUTTON2, GIF = range(4)

reply_keyboard = [
    ["Photo"],
    ['Gif'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "What would you like to receive?",
        reply_markup=markup,
    )
    return CHOOSING


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    return BUTTON


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def random_img():
        n = random.randint(1, 10000000)
        url = f'https://picsum.photos/{query.data}?random={str(n)}'
        return url
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=random_img())
    return CHOOSING


async def gif(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            InlineKeyboardButton("Love", callback_data="love"),
            InlineKeyboardButton("Sport", callback_data="sport"),
            InlineKeyboardButton("Meme", callback_data="meme"),
        ],
        [InlineKeyboardButton("Random", callback_data="&")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose theme:", reply_markup=reply_markup)
    return BUTTON2

async def button2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def gify():
        contents = requests.get(
            f'https://api.giphy.com/v1/gifs/random?api_key=HEpBPk8ptZEhZTuiLsyZutBJxDMZDrst&tag={query.data}rating=pg-13').json()
        data = contents['data']
        url = data['bitly_url']
        return url
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(gify())
    return CHOOSING


def main() -> None:
    application = Application.builder().token("5560967942:AAHdVlB1vMfEwmU1Fl5-NwmtYtgq_Omo3SM").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Photo)$"), photo
                ),
                MessageHandler(filters.Regex("^Gif$"), gif),
            ],
            BUTTON: [CallbackQueryHandler(button)],
            BUTTON2: [CallbackQueryHandler(button2)]
        },
        fallbacks=[MessageHandler(filters.Regex("^Start$"), start)],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()