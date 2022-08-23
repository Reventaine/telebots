import logging
from bs4 import BeautifulSoup
import requests

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
from telegram import  Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


TYPING_ARTIST, TYPING_SONG = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text=f'Hello! Enter an artist name please.')
    return TYPING_ARTIST


async def get_artist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    artist = str(update.message.text).replace(' ', '-')
    context.user_data["artist"] = artist
    await update.message.reply_text(f'Great! Now enter a name of their song.')
    return TYPING_SONG


async def get_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    artist = context.user_data["artist"]
    songname = str(update.message.text).replace(' ', '-')

    def get_lyric():
        url = f"https://www.letras.mus.br/{artist}/{songname}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        lyric = soup.find("div", {"class": "cnt-letra p402_premium"})
        lyrics = str(lyric).replace('<div class="cnt-letra p402_premium">', "") \
            .replace("</div>", "") \
            .replace("<br/>", "\n") \
            .replace("</br>", "\n") \
            .replace("<br>", "\n") \
            .replace("</br>", "\n") \
            .replace("</p><p>", "\n\n") \
            .replace("</p>", "") \
            .replace("<p>", "").strip()
        return lyrics


    await update.message.reply_text(f"*{str(artist).replace('-', ' ').upper()} \- {songname.replace('-', ' ').capitalize()}*", parse_mode='MarkdownV2')
    await update.message.reply_text(get_lyric())

    context.user_data.clear()
    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Start again soon!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5453334258:AAGTg24fHyY_WpuB6Cc8uo2hWBtjJN-nhzM").build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TYPING_ARTIST: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^/done$")), get_artist
                )
            ],
            TYPING_SONG: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^/done$")), get_song
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^/done$"), done)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()