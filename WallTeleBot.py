import logging, random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
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
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def wallpaper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            InlineKeyboardButton("Phone", callback_data="1284/2778"),
            InlineKeyboardButton("iPad", callback_data="1640/2360"),
        ],
        [InlineKeyboardButton("Desktop", callback_data="4096/2160")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_user.send_message(text="Please choose device:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    query = update.callback_query

    def random_img():
        n = random.randint(1, 10000)
        url = f'https://picsum.photos/{query.data}?random={str(n)}'
        return url

    await query.answer()
    await query.edit_message_text('Searching for an awesome wallpaper...')

    try:
        await query.message.reply_photo(random_img())
        await query.edit_message_text('This is your wallpaper:')

    except TimedOut:

        await query.edit_message_text("This might take a while...")

        try:
            await query.message.reply_photo(random_img())
            await query.edit_message_text('This is your wallpaper:')

        except TimedOut:
            await query.edit_message_text(f'Something went wrong :(\nTry again')

    finally:
        return await wallpaper(update, context)


if __name__ == '__main__':
    application = Application.builder().token("TOKEN").build()
    application.add_handler(CommandHandler("Wallpaper", wallpaper))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()
