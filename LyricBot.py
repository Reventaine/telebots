import logging
import requests
import lyricsgenius as lyricg

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
from telegram import Update
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

genius = lyricg.Genius("TOKEN", skip_non_songs=True,
                       excluded_terms=["(Remix)", "(Live)"], remove_section_headers=False, verbose=True, retries=10)

TYPING_ARTIST, TYPING_SONG, TYPING_LYRIC = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text=f'Hello! Enter an artist name please.')
    return TYPING_ARTIST


async def get_artist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    artist = update.message.text
    context.user_data["artist"] = artist
    await update.message.reply_text(f'Great! Now enter a name of their song.')
    return TYPING_SONG


async def get_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    artist = context.user_data["artist"]
    songname = update.message.text
    song = genius.search_song(artist, songname)

    def get_lyric():
        return song.lyrics.replace("Lyrics", '\r\n\r\n') \
            .replace("3Embed", "") \
            .replace("Embed", "") \
            .replace(songname.capitalize(), "", 1)

    def cover():
        cover_art = song.song_art_image_thumbnail_url
        return cover_art

    await update.message.reply_text(f"*{artist.upper()} \- {songname.capitalize()}*", parse_mode='MarkdownV2')
    await update.message.reply_photo(cover())
    await update.message.reply_text(get_lyric())

    context.user_data.clear()
    return ConversationHandler.END


async def lyricsearch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f'Hello! Enter some lyrics to find.')
    return TYPING_LYRIC


async def bylyrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    lyricp = update.message.text

    def get_titles():
        result = []
        request = genius.search_all(lyricp)
        for hit in request['sections'][0]['hits']:
            result.append(hit['result']['full_title'])
        titles = '\r\n'.join(result)
        return titles

    await update.message.reply_text(f'''This is the songs with "{lyricp}" piece of lyrics:''')
    await update.message.reply_text(get_titles())
    return ConversationHandler.END


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f'Hello!'
                                    f'\r\nWith my help you can find lyrics for a songs'
                                    f' - just /start,'
                                    f' \r\nOR you can find a songs FROM lyrics'
                                    f' - /lyricsearch.'
                                    f'\r\nIf you meet any trouble - /done and restart.'
                                    f'\r\nThank you!')


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Start again soon!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""

    application = Application.builder().token("TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("lyricsearch", lyricsearch)],
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
            TYPING_LYRIC: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^/done$")), bylyrics
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^/done$"), done)],
    )


    application.add_handler(CommandHandler("Help", help))

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
