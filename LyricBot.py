import logging
import lyricsgenius as lyricg
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


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


genius = lyricg.Genius('GENIUSTOKEN', skip_non_songs=True,
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


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        song = genius.search_song(artist, songname)

        text = song.lyrics.replace("Lyrics", '\r\n\r\n') \
                .replace("3Embed", "") \
                .replace("Embed", "") \
                .replace(songname.title(), "", 1)

        cover = song.song_art_image_thumbnail_url

        await update.effective_user.send_message(f"*{artist.title()} \- {songname.title()}*", parse_mode='MarkdownV2')

        await update.effective_user.send_photo(cover)
        await update.effective_user.send_message(text)

    except:
        await update.effective_user.send_message(f"Song not found or has no lyrics")


async def get_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global artist, songname
    artist = context.user_data["artist"]
    songname = update.message.text

    await get_text(update, context)


async def spotify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        spoty = SpotifyOAuth(client_id="CLIENT_ID",
                                        client_secret="CLIENT_SECRET",
                                        redirect_uri="URI",
                                        scope="user-read-currently-playing",
                                        username=update.effective_user.id,
                                        open_browser=False)

        sp = spotipy.Spotify(auth_manager=spoty)

        results3 = sp.current_user_playing_track()
        global songname, artist
        songname = (results3['item']['name'])
        artist = (results3['item']['artists'][0]['name'])

        await get_text(update, context)

    except:
        await update.effective_user.send_message(f"Nothing is playing or current song has no lyrics")


async def lyricsearch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f'Hello! Enter some lyrics to find.')
    return TYPING_LYRIC


async def bylyrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lyricp = update.message.text

    result = []
    result2 = []
    piece = []

    try:
        request = genius.search_all(lyricp)
        for hit in request['sections'][0]['hits']:
            result.append(hit['result']['full_title'])
            piece.append(hit['highlights'][0]['value'])
        for hit in request['sections'][1]['hits']:
            result2.append(hit['result']['full_title'])

        await update.message.reply_text(f'''This is the songs with "{lyricp}" piece of lyrics:''')

        for index, item in enumerate(result):
            await update.effective_user.send_message(f'{index+1}) {item} \n\n...{piece[index]}...')
        for index, item in enumerate(result2, start=4):
            await update.effective_user.send_message(f'{index}) {item}')

        return ConversationHandler.END

    except: await update.message.reply_text("Something went wrong")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f'Hello!'
                                    f'\r\nWith my help you can find lyrics for a songs'
                                    f' - /start,'
                                    f'\r\nSearch lyrics for current playing spotify song - /spotify'
                                    f' \r\nOR you can find a songs FROM lyrics'
                                    f' - /lyricsearch.'
                                    f'\r\nIf you meet any trouble - /done and restart.')
    context.user_data.clear()
    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Restart!")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token("TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("lyricsearch", lyricsearch)],
        states={
            TYPING_ARTIST: [
                MessageHandler(
                    filters.TEXT, get_artist
                )
            ],
            TYPING_SONG: [
                MessageHandler(
                    filters.TEXT, get_song
                )
            ],
            TYPING_LYRIC: [
                MessageHandler(
                    filters.TEXT, bylyrics,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^/done$"), done)], allow_reentry=True,
    )
    application.add_handler(CommandHandler("done", done))
    application.add_handler(CommandHandler("Help", help))
    application.add_handler(CommandHandler("spotify", spotify))
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
