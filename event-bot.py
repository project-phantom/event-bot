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
from dbhelper import DB

try:
    from config import TOKEN
except:
    pass

#import 'src\model\user.py'

# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level = logging.ERROR)

logger = logging.getLogger(__name__)

#temporary store of info 
INFO_STORE = {}

#Set up telegram token 
# TELEGRAM_TOKEN = os.environ['HACKNROLLTOKEN'] 
if TOKEN:
    TELEGRAM_TOKEN = TOKEN ##os.environ['HACKNROLLTOKEN'] 
else:
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
einfo = emojize(":information_source: ", use_aliases=True)

# initialize states
(AFTER_START, LOGIN, FIRST_NAME, LAST_NAME, NEWLOGIN, AFTER_DASHBOARD, AFTER_MARK_ATTENDANCE, AFTER_BROWSE_EVENTS, AFTER_MANAGE_EVENTS, AFTER_ADMIN_PANEL, RETURN_ADMIN_PANEL) = range(11)

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


# placeholder cancel 
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
    print(userinput)
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
    print(userinput)
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


# for new users: show token for future logins 
def showtoken(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = html.escape(update.message.text.strip())
    logger.info(userinput)
    print(userinput)
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


"""
0. Main Dashboard 

"""

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
        print(userinput)

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


"""
1. Marking of attendance function
- Scan qr code
- Decode qr code and mark user attendance on database 

"""

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


"""
2. user browsing of events 
- view list of published events 
- sign up for published events 

"""  

def browse_events(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    # CHECK WITH DATABASE HERE 
    # IF EVENT IS PUBLISHED AND APPROVED, IT WILL BE LISTED HERE
    published_events = "PAKORN YOUR JOB"

    EVENTLIST = "INSERT EVENT HERE"

    
    replytext = "<b>Sup! List of cool events going on recently</b>:"
    replytext += "\n\n" + EVENTLIST
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_BROWSE_EVENTS



"""
3. managing events
- creating events
- editing events
- confirming events

"""  
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





"""
4. admin panel functions
"""

# function called by admin_panel to get event and venues that are all pending 
def getPendingEventsVenues():
    list_pending_events = ['EVENT 1', 'EVENT 2', 'EVENT 3']
    list_pending_venues = ['VENUE 1', 'VENUE 2', 'VENUE 3']
    list_eventIDs = ['1234', '1040', '0534']
    list_venueIDs = ['1204', '1200', '0134']
    return list_pending_events, list_pending_venues, list_eventIDs, list_venueIDs


def admin_panel(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    # GET EVENTS AND VENUES REQUESTS CALL FROM FUNCTIONS 
    list_pending_events, list_pending_venues, list_eventIDs, list_venueIDs = getPendingEventsVenues()

    ADMIN_MENU_MESSAGE = "\n\n" + einfo + "<b>List of Event Publications to be Approved:</b>"
    for i in range(len(list_pending_events)):
        ADMIN_MENU_MESSAGE += "\n\n<b>EVENT ID: " + str(list_eventIDs[i]) + "</b>"
        ADMIN_MENU_MESSAGE += "\n\n" + str(list_pending_events[i]) 
        ADMIN_MENU_MESSAGE += "\n\n" +"/approveEvent" + list_eventIDs[i] + " | " +  "/rejectEvent" + list_eventIDs[i] 

    ADMIN_MENU_MESSAGE += "\n\n" + einfo + "<b>List of Venue Bookings to be Approved:</b>"
    for i in range(len(list_pending_venues)):
        ADMIN_MENU_MESSAGE += "\n\n<b>VENUE ID: " + str(list_venueIDs[i]) + "</b>"
        ADMIN_MENU_MESSAGE += "\n\n" + str(list_pending_venues[i])
        ADMIN_MENU_MESSAGE += "\n\n" + "/approveVenue" + list_venueIDs[i] + " | " +  "/rejectVenue" + list_venueIDs[i] 
    
    replytext = "<b>Here is the full list of pending events publication and venue booking requests for you to approve.</b>"
    replytext += ADMIN_MENU_MESSAGE
    
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_ADMIN_PANEL


# update database, delete previous admin panel msg, ask user to press ok and trigger returning to new admin panel
def admin_process_event(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='OK', callback_data = 'return_admin_panel')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    replytext = "Okay! Your previous decision has been recorded. Press 'OK' to return to the Admin Panel."

    if userinput[:-5] == 'approveEvent':
        logger.info("Admin has approved event")
        # PROCESS APPROVE WITH DATABASE HERE

    elif userinput[:-5] == 'rejectEvent':
        logger.info("Admin has rejected event")
        # PROCESS REJECT WITH DATABASE HERE
 
    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])
    return 


def admin_process_venue(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)
    print(userinput)

    button_list = [InlineKeyboardButton(text='OK', callback_data = 'return_admin_panel')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    replytext = "Okay! Your previous decision has been recorded. Press 'OK' to return to the Admin Panel."

    if userinput[:-5] == 'approveVenue':
        logger.info("Admin has approved venue")
        # PROCESS APPROVE WITH DATABASE HERE

    elif userinput[:-5] == 'rejectVenue':
        logger.info("Admin has approved venue")
        # PROCESS REJECT WITH DATABASE HERE
 
    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])
    return


def log_out(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)
    print(userinput)
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

    list_pending_events, list_pending_venues, list_eventIDs, list_venueIDs = getPendingEventsVenues()
    # create unique command for each approval and rejection of the events and venue bookings:
    for i in range(len(list_eventIDs)):
        approvecommandtext = 'approveEvent' + str(list_eventIDs[i])
        rejectcommandtext = 'rejectEvent' + str(list_eventIDs[i])
        dispatcher.add_handler(CommandHandler(command = approvecommandtext, callback = admin_process_event))
        dispatcher.add_handler(CommandHandler(command = rejectcommandtext, callback = admin_process_event))
    for i in range(len(list_venueIDs)):
        approvecommandtext = 'approveVenue' + str(list_venueIDs[i])
        rejectcommandtext = 'rejectVenue' + str(list_venueIDs[i])
        dispatcher.add_handler(CommandHandler(command = approvecommandtext, callback = admin_process_venue))
        dispatcher.add_handler(CommandHandler(command = rejectcommandtext, callback = admin_process_venue))

    dispatcher.add_handler(CallbackQueryHandler(callback = admin_panel, pattern = '^(return_admin_panel)$'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
