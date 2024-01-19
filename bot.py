from dotenv import load_dotenv
import requests
import os
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes


load_dotenv()



f = open('accounts.json')

data = json.load(f)

keyboard = [
    [
        InlineKeyboardButton(f"Запустить {i.get('name')}", callback_data=i.get('account_id')) for i in data
    ],

]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user


    await update.message.reply_html(
        'Запустить?',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query


    # CallbackQueries need to be answered, even if no notification to the user is needed

    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    await query.answer()

    f = open('accounts.json')

    data = json.load(f)

    url = os.getenv("API_URL")+"process_cookie/"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("USER_TOKEN")}'
        }

    payload=[pl for pl in data if str(pl.get('account_id')) == str(query.data)][0]
    try:

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

        reply = ''
            
        print(response.status_code)
        if(response.status_code == 405):
            reply = 'Сервер занят'
        
        if(query.message.text == 'Сервер занят' and reply == 'Сервер занят'):
            reply = "Всё еще занят!"
                
        await query.edit_message_text(text=reply, reply_markup=InlineKeyboardMarkup(keyboard),)
    
    except:
        await query.edit_message_text(text=reply, reply_markup="Скорее всего всё окей и запустилось")




def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv('TOKEN')).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    application.add_handler(CallbackQueryHandler(button))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()