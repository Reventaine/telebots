import logging
import lyricsgenius as lyricg
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from github import Github
from youtubesearchpython import VideosSearch
import yt_dlp
import json
from config import githubToken as githubToken, \
    geniusToken as geniusToken, \
    telegramToken as telegramToken, \
    client_id as client_id, \
    client_secret as client_secret, \
    redirect_uri as redirect_url, \
    url as url

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

github = Github(githubToken)
repository = github.get_user().get_repo('cache-spotify')
contents = repository.get_contents("")

genius = lyricg.Genius(geniusToken, skip_non_songs=True,
                       excluded_terms=["(Remix)", "(Live)"], remove_section_headers=False, verbose=True, retries=10)

TYPING_LYRIC, TOKEN = range(2)


def getAudio():
    videoSearch = VideosSearch(f'{artist} {songname}', limit=1)

    video_url = videoSearch.result()['result'][0]['link']

    filename = f"{artist} - {songname}"
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_url)

    return open(f"{artist} - {songname}", 'rb')


async def songlyrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id,
                                                                             client_secret=client_secret))

    try:
        result = sp.search(q=update.message.text, limit=1, type='track')

        global artist, songname
        artist = result['tracks']['items'][0]['artists'][0]['name']
        songname = result['tracks']['items'][0]['name']

        return await get_text(update, context)

    except IndexError:
        await update.message.reply_text(f"Song not found or has no lyrics")


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        song = genius.search_song(artist, songname)

        text = song.lyrics.replace("Lyrics", '\r\n\r\n') \
            .replace("3Embed", "") \
            .replace("Embed", "") \
            .replace(songname.title(), "", 1) \

        if text[-2].isdigit():
            text = text[:-2]

        elif text[-1].isdigit():
            text = text[:-1]

        cover = song.song_art_image_thumbnail_url

        await update.message.reply_photo(cover,
                                         caption=f"<b>{artist.title()}</b> - <b>{songname.title()}</b>",
                                         parse_mode='HTML')

        await update.message.reply_text(text)

        if update.message.text != "/spotify":
            await update.message.reply_audio(getAudio())


async def spotify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global songname, artist
    try:
        file = repository.get_contents(f'.cache-{update.effective_user.id}')
        f = open(f'.cache-{update.effective_user.id}', 'w')
        f.write(file.decoded_content.decode())
        f.close()

        cache_handler = spotipy.cache_handler.CacheFileHandler(username=update.effective_user.id)
        auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_url,
                                                   scope="user-read-currently-playing",
                                                   cache_handler=cache_handler,
                                                   show_dialog=True)

        sp = spotipy.Spotify(auth_manager=auth_manager)

        results3 = sp.current_user_playing_track()
        songname = (results3['item']['name'])
        artist = (results3['item']['artists'][0]['name'])

        await get_text(update, context)

    except spotipy.exceptions.SpotifyException and json.decoder.JSONDecodeError:
        await update.message.reply_text(
            f'Please go here and send link back to this chat: \n[SPOTIFY LOG IN]({url})', parse_mode='MarkdownV2')
        return TOKEN

    except TypeError:
        await update.message.reply_text(f"Song not found or has no lyrics")


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
            await update.effective_user.send_message(f'{index + 1}) {item} \n\n...{piece[index]}...')
        for index, item in enumerate(result2, start=4):
            await update.effective_user.send_message(f'{index}) {item}')

        return ConversationHandler.END

    except:
        await update.message.reply_text("Something went wrong")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f'Hello!'
                                    f'\r\nEnter name of the song to get lyrics and audio.'
                                    f'You can enter piece of lyrics of the song and get full lyrics.'
                                    f'Also you can log in with Spotify and get lyrics for your current playing song.')

    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Restart!")
    return ConversationHandler.END


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logo = 'https://raw.githubusercontent.com/Reventaine/cache-spotify/main/Spotify_logo_with_text.svg.png?' \
           'token=GHSAT0AAAAAABX435PSOGJKACUPKFC6D34OYY2JLCA'
    await update.message.reply_photo(photo=logo,
                                     caption=f'Please go here and send link back to this chat: '
                                             f'\n[SPOTIFY LOG IN]({url})', parse_mode='MarkdownV2')
    return TOKEN


def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    spoty = spotipy.SpotifyOAuth(client_id=client_id,
                                 client_secret=client_secret,
                                 redirect_uri=redirect_url,
                                 scope="user-read-currently-playing",
                                 username=update.effective_user.id,
                                 open_browser=False)

    code = codeR
    f = open(f'.cache-{update.effective_user.id}', 'w')
    tokenJS = json.dumps(spoty.get_access_token(code=code, as_dict=True, check_cache=False))
    f.write(tokenJS)
    cachesUpdated = []
    for content_file in contents:
        cachesUpdated.append(content_file)
    if f'.cache-{update.effective_user.id}' in str(cachesUpdated):
        contentCache = repository.get_contents(f'.cache-{update.effective_user.id}')
        repository.update_file(f'.cache-{update.effective_user.id}', 'update token', tokenJS, contentCache.sha,
                               branch="main")
    else:
        repository.create_file(f'.cache-{update.effective_user.id}', "create_token", tokenJS)

    f.close()


async def token2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global codeR
    # Get the authorization verifier code from the callback url
    text = update.message.text
    codeR = text.replace('http://127.0.0.1:9090/?code=', '')
    get_token(update, context)
    await update.message.reply_text('Success. \nNow you can use /spotify function')


def main() -> None:
    application = Application.builder().token(telegramToken).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("lyricsearch", lyricsearch),
            CommandHandler("token", token),
            CommandHandler("spotify", spotify)
        ],
        states={
            TYPING_LYRIC: [
                MessageHandler(
                    filters.TEXT, bylyrics,
                )
            ],
            TOKEN: [
                MessageHandler(
                    filters.TEXT, token2,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^/done$"), done), CommandHandler("token", token)], allow_reentry=True,
    )
    application.add_handler(CommandHandler("done", done))
    application.add_handler(CommandHandler("Help", help))
    application.add_handler(MessageHandler(filters.TEXT & (~ filters.COMMAND), songlyrics))
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
