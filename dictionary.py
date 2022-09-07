import json, requests
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, filters, MessageHandler

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
    words = update.message.text.lower()
    api = f'https://api.dictionaryapi.dev/api/v2/entries/en/{words}'

    try:
        re = requests.get(api).text
        wordlist = json.loads(re)
        for i in range(len(wordlist)):
            word = wordlist[i]
            # get word and phonetic if later exists:
            await update.message.reply_text('📚📚📚📚📚')
            if not word.get('phonetic') is None:
                try:
                    await update.message.reply_text(f'*{words.title()}* 📖'
                                                    f'\nPhonetic:  *{word["phonetic"]}*', parse_mode='MarkdownV2')
                except:
                    await update.message.reply_text(f'{words.title()}'
                                                    f'\nPhonetic:  {word["phonetic"]}')
            else:
                await update.message.reply_text(f'*{words.title()}*', parse_mode='MarkdownV2')

            # get audio
            for i in word['phonetics']:
                if 'uk' in str(i['audio']):
                    await update.message.reply_audio(audio=i['audio'])
                if 'us' in str(i['audio']):
                    await update.message.reply_audio(audio=i['audio'])

            # get definitions:
            for i in word['meanings']:

                if i["partOfSpeech"] == 'noun':
                    await update.message.reply_text('*Noun* 📘', parse_mode='MarkdownV2')
                    for index, n in enumerate(i["definitions"][:3], start=1):
                        if n.get("example") is not None:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}\n\n'
                                                            f'Example:  {n.get("example")}')
                        else:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}')

                elif i["partOfSpeech"] == 'verb':
                    await update.message.reply_text('*Verb* 📗', parse_mode='MarkdownV2')
                    for index, n in enumerate(i["definitions"][:3], start=1):
                        if n.get("example") is not None:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}\n\n'
                                                            f'Example:  {n.get("example")}')
                        else:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}')

                elif i["partOfSpeech"] == 'adjective 📕':
                    await update.message.reply_text('*Adjective* ', parse_mode='MarkdownV2')
                    for index, n in enumerate(i["definitions"][:3], start=1):
                        if n.get("example") is not None:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}\n\n'
                                                            f'Example:  {n.get("example")}')
                        else:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}')

                elif i["partOfSpeech"] == 'adverb 📙':
                    await update.message.reply_text('*Adverb*', parse_mode='MarkdownV2')
                    for index, n in enumerate(i["definitions"][:3], start=1):
                        if n.get("example") is not None:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}\n\n'
                                                            f'Example:  {n.get("example")}')
                        else:
                            await update.message.reply_text(f'{index}) Definition:  {n["definition"]}')

    except KeyError:
        await update.message.reply_text('There is no such word found in dictionary!')


if __name__ == '__main__':
    application = Application.builder().token("5522209665:AAFtjdsSqMFG04zwaX-FE-6oFHVpCeJ1ilU").build()
    application.add_handler(MessageHandler(filters.TEXT, start))
    application.run_polling()


