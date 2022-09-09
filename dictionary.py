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


def random_word():
    url = "https://random-words5.p.rapidapi.com/getRandom"

    headers = {
        "X-RapidAPI-Key": "014eefd150mshba5089faf565a46p13f492jsn3b657ae08e0c",
        "X-RapidAPI-Host": "random-words5.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    return response.text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 # dictionary API:
    words = update.message.text.lower()
    if words == 'random_word':
        words = random_word()
    api = f'https://api.dictionaryapi.dev/api/v2/entries/en/{words}'

 # imagesearch API:

    imageapi = "https://bing-image-search1.p.rapidapi.com/images/search"

    querystring = {"q": f"{words}", "count": "10"}

    headers = {
        "X-RapidAPI-Key": "014eefd150mshba5089faf565a46p13f492jsn3b657ae08e0c",
        "X-RapidAPI-Host": "bing-image-search1.p.rapidapi.com"
    }

    response = requests.request("GET", imageapi, headers=headers, params=querystring)

    images = json.loads(response.text)['value']

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

            # insert photo:
            try:
                await update.message.reply_photo(images[i]["thumbnailUrl"])
            except:
                await update.message.reply_text('📖📖📖📖📖')

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

async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    quotesapi = "https://quotes15.p.rapidapi.com/quotes/random/"

    headers = {
            "X-RapidAPI-Key": "014eefd150mshba5089faf565a46p13f492jsn3b657ae08e0c",
            "X-RapidAPI-Host": "quotes15.p.rapidapi.com"
        }

    response = requests.request("GET", quotesapi, headers=headers)

    quote = json.loads(response.text)['content']
    author = json.loads(response.text)['originator']['name']
    url = f'https://picsum.photos/400/100?random=10200'

    await update.message.reply_photo(photo=url, caption=f'"{quote}" \n\n-{author}')


async def collocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    return await collocation2(update, context)

async def collocation2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.lower().replace("/collocation ", "")
    response = requests.request("GET", f'https://lt-collocation-test.herokuapp.com/todos/?query={query}&lang=en')
    collocations = json.loads(response.text)
    for i in range(len(collocations)):
        await update.message.reply_text(f"📝📝📝📝📝\n"
                                        f"Collocation: {collocations[i]['collocation']}\n"
                                        f"Example: {collocations[i]['examples'][0].replace('</b>', '').replace('<b>', '')}\n")


async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://random-facts2.p.rapidapi.com/getfact"

    headers = {
        "X-RapidAPI-Key": "014eefd150mshba5089faf565a46p13f492jsn3b657ae08e0c",
        "X-RapidAPI-Host": "random-facts2.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    fact = json.loads(response.text)["Fact"]
    fact = fact[0].lower() + fact[1:]

    await update.message.reply_text(f'🧐🧐🧐🧐🧐\nFact: {fact}')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Use list of commands!\n'
                                    f'/collocation (word) will give you collocations for given word.\n'
                                    f'Just send any word for definitions.')


if __name__ == '__main__':
    application = Application.builder().token("5522209665:AAFtjdsSqMFG04zwaX-FE-6oFHVpCeJ1ilU").build()
    application.add_handler(MessageHandler(filters.TEXT & (~ filters.COMMAND), start))
    application.add_handler(CommandHandler("quote", quotes))
    application.add_handler(CommandHandler("collocation", collocation))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()


