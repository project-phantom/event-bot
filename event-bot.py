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

#import 'src\model\user.py'

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

# emojis
eheart = emojize(":heart: ", use_aliases=True)

# initialize states
(AFTER_START, LOGIN, FIRST_NAME, LAST_NAME, NEWLOGIN, AFTER_DASHBOARD) = range(6)


def start(bot, update):
    button_list = [InlineKeyboardButton(text='Register', callback_data = 'register'),
                    InlineKeyboardButton(text='Login', callback_data = 'login')]
    menu = build_menu(button_list, n_cols = 2, header_buttons = None, footer_buttons = None)
    replytext = "Welcome to the NUS Events Management System. If you are new, please register a new user token."

    try:
        user = update.message.from_user
        chatid = update.message.chat.id
        userinput = html.escape(update.message.text.strip())
        logger.info(userinput)
        
        # if new, set up info_store
        INFO_STORE[user.id] = {}
        INFO_STORE[user.id]["BotMessageID"] = []

        msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
        #appends message sent by bot itself - the very first message: start message
        INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    except AttributeError:
        query = update.callback_query
        user = query.from_user
        chatid = query.message.chat.id
        messageid = query.message.message_id
        userinput = html.escape(query.data)
        logger.info(userinput)

        bot.editMessage(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_START


def login(bot, update):
    query = update.callback_query
    user = query.from_user
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "<b>Please type and send your unique token ID:</b>"
        
    bot.editMessage(text = replytext,
                    chat_id = chatid,
                    message_id = messageid,
                    reply_markup = InlineKeyboardMarkup(menu),
                    parse_mode=ParseMode.HTML)
    return LOGIN


def register(bot, update):
    query = update.callback_query
    user = query.from_user
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "What is your <b>First Name</b>?"
        
    bot.editMessage(text = replytext,
                    chat_id = chatid,
                    message_id = messageid,
                    reply_markup = InlineKeyboardMarkup(menu),
                    parse_mode=ParseMode.HTML)
    return FIRST_NAME

def lastname(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = html.escape(update.message.text.strip())
    logger.info(userinput)

    INFO_STORE[user.id]['first_name'] = userinput

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "How about your <b>Last Name</b>?"
    
    # deletes message sent previously by bot
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])
    
    return LAST_NAME

def showtoken(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = html.escape(update.message.text.strip())
    logger.info(userinput)

    INFO_STORE[user.id]['last_name'] = userinput

    button_list = [InlineKeyboardButton(text='Login Now', callback_data = 'dashboard'),
                    InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 2, header_buttons = None, footer_buttons = None)
    
    replytext = "Okay! Your information is registered. The following is your user token, please keep it safely! Write it down somewhere :)"
    replytext += "\n\nYour unique User Token: "
    USERTOKEN = "123"
    replytext += USERTOKEN

    # deletes message sent previously by bot
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return NEWLOGIN


def dashboard(bot, update):
    query = update.callback_query
    user = query.from_user
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Mark Attendance', callback_data = 'attendance'),
                    InlineKeyboardButton(text='Browse Events', callback_data = 'browse_events'),
                    InlineKeyboardButton(text='Manage Events', callback_data = 'manage_events'),
                    InlineKeyboardButton(text='Admin Panel', callback_data = 'admin_panel'),
                    InlineKeyboardButton(text='Log Out', callback_data = 'log_out')]

    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "DASHBOARD:"
        
    bot.editMessage(text = replytext,
                    chat_id = chatid,
                    message_id = messageid,
                    reply_markup = InlineKeyboardMarkup(menu),
                    parse_mode=ParseMode.HTML)

    return AFTER_DASHBOARD


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher=updater.dispatcher
    job_queue = updater.job_queue  
    dispatcher.add_error_handler(error)

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],

        states = {
            AFTER_START: [CallbackQueryHandler(callback = login, pattern = 'login'),
                            CallbackQueryHandler(callback = register, pattern = 'register')],

            LOGIN: [CallbackQueryHandler(callback = dashboard, pattern = 'dashboard'),
                    CallbackQueryHandler(callback = start, pattern = 'back')],

            FIRST_NAME: [MessageHandler(filters.text, lastname)
                        CallbackQueryHandler(callback = start, pattern = 'back')],

            LAST_NAME: [MessageHandler(filters.text, showtoken)
                        CallbackQueryHandler(callback = register, pattern = 'back')],

            NEWLOGIN: [CallbackQueryHandler(callback = dashboard, pattern = 'dashboard'),
                        CallbackQueryHandler(callback = showtoken, pattern = 'back')], 

            AFTER_DASHBOARD: [CallbackQueryHandler(callback = dashboard, pattern = 'attendance'),
                            CallbackQueryHandler(callback = dashboard, pattern = 'browse_events'),
                            CallbackQueryHandler(callback = dashboard, pattern = 'manage_events'),
                            CallbackQueryHandler(callback = dashboard, pattern = 'admin_panel'),
                            CallbackQueryHandler(callback = dashboard, pattern = 'log_out')]
        }
        fallbacks = [CommandHandler('cancel', cancel)],
        allow_reentry = True
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()