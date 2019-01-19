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
(AFTER_START, LOGIN, FIRST_NAME, LAST_NAME, NEWLOGIN, AFTER_DASHBOARD, AFTER_MARK_ATTENDANCE, AFTER_BROWSE_EVENTS, AFTER_MANAGE_EVENTS, AFTER_ADMIN_PANEL) = range(10)

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

        bot.editMessageText(text = replytext,
                            chat_id = chatid,
                            message_id = messageid,
                            reply_markup = InlineKeyboardMarkup(menu),
                            parse_mode=ParseMode.HTML)
    return AFTER_START


def cancel(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    logger.info("User {} cancelled the conversation.".format(user.username if user.username else user.first_name))
    
    # deletes message sent previously by bot
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])
    
    bot.send_message(text = "Bye! Press /start if you wish to restart the whole process!",
                     chat_id=chatid,
                     parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def login(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "<b>Please type and send your unique token ID:</b>"
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return LOGIN


def register(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "What is your <b>First Name</b>?"
        
    bot.editMessageText(text = replytext,
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
    INFO_STORE[user.id]['user_token'] = USERTOKEN

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
    button_list = [InlineKeyboardButton(text='Mark Attendance', callback_data = 'attendance'),
                    InlineKeyboardButton(text='Browse Events', callback_data = 'browse_events'),
                    InlineKeyboardButton(text='Manage Events', callback_data = 'manage_events'),
                    InlineKeyboardButton(text='Admin Panel', callback_data = 'admin_panel'),
                    InlineKeyboardButton(text='Log Out', callback_data = 'log_out')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    replytext = "<b>DASHBOARD:</b>"

    try:
        user = update.message.from_user
        chatid = update.message.chat.id
        userinput = html.escape(update.message.text.strip())
        logger.info(userinput)

        USERTOKEN = userinput
        INFO_STORE[user.id]['user_token'] = USERTOKEN

        # deletes message sent previously by bot
        bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

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
        
        bot.editMessageText(text = replytext,
                            chat_id = chatid,
                            message_id = messageid,
                            reply_markup = InlineKeyboardMarkup(menu),
                            parse_mode=ParseMode.HTML)

    return AFTER_DASHBOARD

def mark_attendance(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    replytext = "Please send me the event QR code as a photograph."
    replytext += "\n\n<b>What should I do</b>?"
    replytext += "\n\n1. Quit Telegram temporarily"
    replytext += "\n\n2. Take a photo of the QR code with your phone camera and save the photo in your phone"
    replytext += "\n\n3. Return to this chat and send me the QR code photo you have taken. Do NOT send as a file!"
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_MARK_ATTENDANCE


def check_QR_code(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message
    logger.info("User has sent QR code.")

    qrcorrect = True

    # deletes message sent previously by bot
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    # if qr code in database
    if qrcorrect == True:
        replytext = "Your event registration has completed. Your attendance is successfully recorded.\n\nEnjoy the event!"
        msgsent = bot.send_message(text = replytext,
                                    chat_id = chatid,
                                    parse_mode=ParseMode.HTML)
        #appends message sent by bot itself - the very first message: start message
        INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])
        return ConversationHandler.END

    else: 
        replytext = "There is some error in the image you have sent. The event has either expired or it does not exist. Please contact the admins for the event if you are unsure.\n\nTo return to the main menu, please press /start."
        msgsent = bot.send_message(text = replytext,
                                    chat_id = chatid,
                                    parse_mode=ParseMode.HTML)
        #appends message sent by bot itself - the very first message: start message
        INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])
        return ConversationHandler.END


def browse_events(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    EVENTLIST = "INSERT EVENT HERE"

    replytext = "<b>Sup! List of cool events going on recently</b>:"
    replytext += "\n\n" + EVENTLIST
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_BROWSE_EVENTS


def manage_events(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    EVENTMANAGEMENTLIST = "LIST OF EVENTS MANAGED HERE"

    replytext = "<b>Here are the list of events you have started:</b>"
    replytext += "\n\n" + EVENTMANAGEMENTLIST
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_MANAGE_EVENTS


def admin_panel(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    ADMIN_MENU_MESSAGE = "LIST OF EVENTS TO BE APPROVED / REJECTED HERE; WITH URL LINKS."

    replytext = "<b>Here are a list of pending events for you to approve:</b>"
    replytext += "\n\n" + ADMIN_MENU_MESSAGE
    
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_ADMIN_PANEL


def log_out(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)
    
    replytext = "Thank you for using the system. Press /start again if you wish to relogin anytime.\n\nGoodbye!"
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher=updater.dispatcher
    dispatcher.add_error_handler(error)

    conv_handler = ConversationHandler(
            entry_points = [CommandHandler('start', start)],

            states = {
                AFTER_START: [CallbackQueryHandler(callback = login, pattern = '^(login)$'),
                            CallbackQueryHandler(callback = register, pattern = '^(register)$')],

                LOGIN: [MessageHandler(Filters.text, dashboard),
                        CallbackQueryHandler(callback = start, pattern = '^(back)$')],

                FIRST_NAME: [MessageHandler(Filters.text, lastname),
                            CallbackQueryHandler(callback = start, pattern = '^(back)$')],

                LAST_NAME: [MessageHandler(Filters.text, showtoken),
                            CallbackQueryHandler(callback = register, pattern = '^(back)$')],

                NEWLOGIN: [CallbackQueryHandler(callback = dashboard, pattern = '^(dashboard)$'),
                            CallbackQueryHandler(callback = showtoken, pattern = '^(back)$')], 

                AFTER_DASHBOARD: [CallbackQueryHandler(callback = mark_attendance, pattern = '^(attendance)$'),
                                CallbackQueryHandler(callback = browse_events, pattern = '^(browse_events)$'),
                                CallbackQueryHandler(callback = manage_events, pattern = '^(manage_events)$'),
                                CallbackQueryHandler(callback = admin_panel, pattern = '^(admin_panel)$'),
                                CallbackQueryHandler(callback = log_out, pattern = '^(log_out)$')],
                
                AFTER_MARK_ATTENDANCE: [CallbackQueryHandler(callback = dashboard, pattern = '^(back)$'),
                                        MessageHandler(Filters.photo, check_QR_code)],

                AFTER_BROWSE_EVENTS: [CallbackQueryHandler(callback = dashboard, pattern = '^(back)$')],

                AFTER_MANAGE_EVENTS: [CallbackQueryHandler(callback = dashboard, pattern = '^(back)$')],

                AFTER_ADMIN_PANEL: [CallbackQueryHandler(callback = dashboard, pattern = '^(back)$')],

            },

            fallbacks = [CommandHandler('cancel', cancel)],
            allow_reentry = True
        )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
