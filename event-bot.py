#import string 
import time
import datetime
import logging
from threading import RLock
from threading import Thread
import os
import sys
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from emoji import emojize
import html


# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level = logging.INFO)

logger = logging.getLogger(__name__)

#temporary store of info 
INFO_STORE = {}

#Set up telegram token 
TELEGRAM_TOKEN = os.environ['HACKNROLLTOKEN'] 

# Building menu for every occasion 
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher=updater.dispatcher
    job_queue = updater.job_queue  
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_error_handler(error)


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()