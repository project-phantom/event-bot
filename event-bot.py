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

from src.model.user import User

# importing calendar module
<<<<<<< HEAD
# import calendar_telegram.telegramcalendar

from calendar_telegram import telegramcalendar
=======
import calendar_telegram.telegramcalendar
>>>>>>> d3f746d9c1b4c116dcdc264b6b452cbe76de9cd5


#try:
#    from config import TOKEN
#except:
#    pass
#Set up telegram token 
if 'HACKNROLLTOKEN' in os.environ:
    TELEGRAM_TOKEN = os.environ['HACKNROLLTOKEN'] 
else:
   from config import TOKEN
   TELEGRAM_TOKEN = TOKEN

#import 'src\model\user.py'

# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level = logging.ERROR)

logger = logging.getLogger(__name__)

#temporary store of info 
INFO_STORE = {}


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
ecross = emojize(":cross: ", use_aliases=True)

# initialize states
(AFTER_START, LOGIN, VERIFY_LOGIN, FIRST_NAME, NEWLOGIN, AFTER_DASHBOARD, AFTER_MARK_ATTENDANCE, AFTER_BROWSE_EVENTS, AFTER_MANAGE_EVENTS, AFTER_START_EDIT_EVENT, CREATE_NEW_EVENT, CREATE_EVENT_DESC, FINAL_CREATE_EVENT, RENAME_EVENT, RENAME_EVENT_CONFIRM, EDIT_EVENT_DESCRIPTION, EDIT_EVENT_DESCRIPTION_CONFIRM, AFTER_ADMIN_PANEL) = range(18)

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


def login_verify(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = html.escape(update.message.text.strip())
    logger.info(userinput)

    USERTOKEN = userinput
    
    if User.login(USERTOKEN): #TEST IF USERTOKEN IS IN DATABASE HERE
        # INFO_STORE[user.id]['user_token'] = USERTOKEN # only record usertoken if success login match
        INFO_STORE['user_token'] = USERTOKEN   ## only record usertoken if success login match
        button_list = [InlineKeyboardButton(text='Go to Dashboard', callback_data = 'login_success')]
        replytext = "<b>Great! You have successfully logged in.</b>"

    else: 
        button_list = [InlineKeyboardButton(text='FILL UP AGAIN', callback_data = 'login_fail')]
        replytext = "<b>ERROR. Your User Token is not found. Please try again or register first.</b>"

    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
    # deletes message sent previously by bot
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return VERIFY_LOGIN  


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
    
    # appends message sent by bot itself - the very first message: start message
    return FIRST_NAME

# def lastname(bot, update):
#     user = update.message.from_user
#     chatid = update.message.chat.id
#     userinput = html.escape(update.message.text.strip())
#     logger.info(userinput)

#     INFO_STORE[user.id]['first_name'] = userinput

#     button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
#     menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
    
#     replytext = "How about your <b>Last Name</b>?"
    
#     # deletes message sent previously by bot
#     bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

#     msgsent = bot.send_message(text = replytext,
#                                 chat_id = chatid,
#                                 reply_markup = InlineKeyboardMarkup(menu),
#                                 parse_mode=ParseMode.HTML)
    
#     #appends message sent by bot itself - the very first message: start message
#     INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])
    
#     return LAST_NAME


# for new users: show token for future logins 
def showtoken(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = html.escape(update.message.text.strip())
    logger.info(userinput)
    print(userinput)
    INFO_STORE[user.id]['first_name'] = userinput
 
    replytext = "Okay! Your information is registered. The following is your user token, please keep it safely! Write it down somewhere :)"
    replytext += "\n\nYour unique User Token: "
    USERTOKEN = User.register(INFO_STORE[user.id]["first_name"])
    INFO_STORE[user.id]['user_token'] = USERTOKEN
    if USERTOKEN:
        replytext += USERTOKEN
        button_list = [InlineKeyboardButton(text='Login Now', callback_data = 'dashboard'),
                    InlineKeyboardButton(text='Back', callback_data = 'back')]

    else: 
        button_list = [InlineKeyboardButton(text='Register AGAIN', callback_data = 'register')]
        replytext = "<b>Same username already existed!</b>"

    
    menu = build_menu(button_list, n_cols = 2, header_buttons = None, footer_buttons = None)

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

# function called by browse_events to get events that are all approved and published
# def getPublishedEvents():
#     published_events_list = ['EVENT 1', 'EVENT 2', 'EVENT 3']
#     published_eventIDs = ['1234', '1040', '0534']
#     return published_events_list, published_eventIDs


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

    # published_events_list, published_eventIDs = getPublishedEvents()
    published_events_list = DB().generate_all_approved_events()

    BROWSE_EVENTS_MESSAGE = ''
    for i in range(len(published_events_list)):
        BROWSE_EVENTS_MESSAGE += "\n\n<b>EVENT ID: " + str(published_events_list[i][0]) + "</b>"
        BROWSE_EVENTS_MESSAGE += "\n\n" + str(published_events_list[i][1]) 
        BROWSE_EVENTS_MESSAGE += "\n\n" +"/registerForEvent" + str(published_events_list[i][0])
    
    replytext = einfo + "<b>Sup! List of cool events going on recently</b>:"
    replytext += "\n\n" + BROWSE_EVENTS_MESSAGE
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)

    return AFTER_BROWSE_EVENTS


def confirm_event_registration(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)
    ## registerForEvent and user_token
    DB().register_for_event(userinput, INFO_STORE['user_token'])

    replytext = "WOOTS! You have successfully registered for this event! Press /start if you wish to return to the main menu :)"

    if userinput[:-5] == 'registerForEvent':
        logger.info("User will be starting registration for this event.")
        # PROCESS APPROVE WITH DATABASE HERE

    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return ConversationHandler.END


"""
3. managing events
a) editing events: renaming and descriptions edit 
b) confirming events
c) setting dates for events 
d) booking venues 
e) creating new events: name and description

"""  
def manage_events(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)
    
    user_list_events = ['1234', '2345'] # INPUT LIST OF USER CREATED EVENTS 
    
    button_list = []
    for i in range(len(user_list_events)):
        buttontext = 'Event ' + user_list_events[i]
        callbackdata = user_list_events[i]
        button_list.append(InlineKeyboardButton(text=buttontext, callback_data = callbackdata))
    
    button_list.append(InlineKeyboardButton(text='Create New Event', callback_data = 'create_event'))
    button_list.append(InlineKeyboardButton(text='Back', callback_data = 'back'))

    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    replytext = einfo + "<b>List of Events You Have Started</b>"
    replytext = "\n\nPlease select the event you wish to add more details for. You can also create a new event."

    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return AFTER_MANAGE_EVENTS


def start_edit_event(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    eventID = userinput

    # stores current event ID and carry it for future edit references 
    INFO_STORE[user.id]['Current_Event_ID'] = eventID

    EVENTMANAGEMENTLIST = "LIST OF EVENTS MANAGED HERE"
    # print(INFO_STORE['user_token'])
    print(INFO_STORE['user_token'])
    list_events = DB().generate_events_of_user(INFO_STORE['user_token'])

    replytext = "<b>Here are the list of events you have started:</b>"
    replytext += "\n\n" + EVENTMANAGEMENTLIST
    for i in range(len(list_events)):
        replytext += "\n\n<b>EVENT ID: " + str(list_events[i][0]) + "</b>"
        replytext += "\n\n" + str(list_events[i][1]) 
        replytext += "\n\n" +"status:" + str(list_events[i][2])

    """ 
    CPF'S CODE:
    """
    # MATCH EVENT ID WITH DATABASE 
    # GET DATABASE EVENT DETAILS:
    event_venue = 'NIL'
    event_timeslots = 'NIL'
    event_status = "NOT APPROVED"

    replytext = einfo + "<b>Showing Information for Event: " + eventID + "</b>"
    replytext += "EVENT INFORMATION FOR PARTICULAR EVENTID"
    replytext += "\n- " + "<b>Event Name: </b>" + "INSERT EVENT NAME"
    replytext += "\n- " + "<b>Description: </b>" + "INSERT EVENT DESCRIPTION"
    replytext += "\n- " + "<b>Venue Booked: </b>" + event_venue
    replytext += "\n- " + "<b>Timeslot Booked: </b>" + event_timeslots
    replytext += "\n- " + "<b>Event Poster: </b>" + "INSERT EVENT CREATOR NAME"
    replytext += "\n- " + "<b>Current Status: </b>" + event_status

    """
    END
    """
    button_list = []
    # add dates row by row 
    for date in selected_dates_list:
        datesrow = []
        datesrow.append(InlineKeyboardButton(date, callback_data=data_ignore))
        canceldatetext = ecross + "Cancel"
        canceldatedata = "canceldate" + date
        datesrow.append(InlineKeyboardButton(text = canceldatetext, callback_data=canceldatedata))
        button_list.append(datesrow)
    
    button_list.append(InlineKeyboardButton(text='Rename Event', callback_data = 'rename_event'))
    button_list.append(InlineKeyboardButton(text='Edit Description', callback_data = 'edit_desc'))
    button_list.append(InlineKeyboardButton(text='Book Venue', callback_data = 'book_venue'))
    button_list.append(InlineKeyboardButton(text='Request Publication', callback_data = 'request_publish'))
    button_list.append(InlineKeyboardButton(text='Back', callback_data = 'back'))

    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(button_list),
                        parse_mode=ParseMode.HTML)

    return AFTER_START_EDIT_EVENT


# part a) renaming and editing event description 
def rename_event(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    # if go back, will callback currently selected event ID
    eventID = INFO_STORE[user.id]['Current_Event_ID'] 
    button_list = [InlineKeyboardButton(text='Back', callback_data = eventID)]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
        
    replytext = "<b>Please send me your new Event Name</b>:"
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return RENAME_EVENT

def cancel_date():
    pass

def process_rename_event(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)

    #neweventname = userinput
    # PROCESS EVENT RENAMING 
    # RECORD NEW EVENT TO DATABASE 

    replytext = "<b>Your new Event Name is saved.</b>"

    eventID = INFO_STORE[user.id]['Current_Event_ID'] 
    button_list = [InlineKeyboardButton(text='Return to Event Page', callback_data = eventID)]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return RENAME_EVENT_CONFIRM


def edit_event_desc(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    # if go back, will callback currently selected event ID
    eventID = INFO_STORE[user.id]['Current_Event_ID'] 
    button_list = [InlineKeyboardButton(text='Back', callback_data = eventID)]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)
        
    replytext = "<bPlease send me your new Event Descriptions</b>:"
        
    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)

    return EDIT_EVENT_DESCRIPTION

def process_event_description_edit(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)

    #neweventdescription = userinput
    # PROCESS EVENT EDIT 
    # RECORD NEW EVENT DESCRIPTION TO DATABASE 

    replytext = "<b>Your new Event Description is saved.</b>"

    eventID = INFO_STORE[user.id]['Current_Event_ID'] 
    button_list = [InlineKeyboardButton(text='Return to Event Page', callback_data = eventID)]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return EDIT_EVENT_DESCRIPTION_CONFIRM


# part b) selecting venue and date for event 
def book_venue(bot, update):
    
    return BOOK_VENUE


def calendar_handler(bot,update):

    update.message.reply_text("Please select a date: ",
                        reply_markup=telegramcalendar.create_calendar())


def inline_handler(bot,update):
    selected,date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        bot.send_message(chat_id=update.callback_query.from_user.id,
                        text="You selected %s" % (date.strftime("%d/%m/%Y")),
                        reply_markup=ReplyKeyboardRemove())


# part c) booking venue 
def book_venue(bot, update):

    return START_BOOK_VENUE



# part d) confirming event and publishing 
def request_publish_event(bot, update):

    return PUBLISH_EVENT_CONFIRMATION




# part e) creating new event
def start_create_event(bot, update):
    query = update.callback_query
    chatid = query.message.chat.id
    messageid = query.message.message_id
    userinput = html.escape(query.data)
    logger.info(userinput)

    button_list = [InlineKeyboardButton(text='Back', callback_data = 'back')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    replytext = "<b>What is your Event Name?</b>"

    bot.editMessageText(text = replytext,
                        chat_id = chatid,
                        message_id = messageid,
                        reply_markup = InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)
    return CREATE_NEW_EVENT


def create_event_name(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)

    replytext = "<b>Please include your Event Description:</b>"

    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return CREATE_EVENT_DESC


def final_create_event(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    userinput = update.message.text.strip()[1:]
    logger.info(userinput)

    replytext = "<b>Great! Your basic Event details are created.</b>"
    replytext += "\n\n<b>The following is your generated Event ID: </b>"
    replytext += "INSERT TOKEN ID" # GENERATE TOKEN 

    button_list = [InlineKeyboardButton(text='Book Venue and Time', callback_data = 'back_to_manage_events')]
    menu = build_menu(button_list, n_cols = 1, header_buttons = None, footer_buttons = None)

    # deletes message sent previously by bot (this is the previous admin panel message)
    bot.delete_message(chat_id=chatid, message_id=INFO_STORE[user.id]["BotMessageID"][-1])

    msgsent = bot.send_message(text = replytext,
                                chat_id = chatid,
                                reply_markup = InlineKeyboardMarkup(menu),
                                parse_mode=ParseMode.HTML)
    
    #appends message sent by bot itself - the very first message: start message
    INFO_STORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return FINAL_CREATE_EVENT


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

    # list_pending_events, list_pending_venues, list_eventIDs, list_venueIDs = getPendingEventsVenues()

    list_events = DB().generate_all_pending_events()

    ADMIN_MENU_MESSAGE = "\n\n" + einfo + "<b>List of Event Publications to be Approved:</b>"
    for i in range(len(list_events)):
        ADMIN_MENU_MESSAGE += "\n\n<b>EVENT ID: " + str(list_events[i][0]) + "</b>"
        ADMIN_MENU_MESSAGE += "\n\n" + str(list_events[i][1]) 
        ADMIN_MENU_MESSAGE += "\n\n" +"/approveEvent" + str(list_events[i][0]) + " | " +  "/rejectEvent" + str(list_events[i][0])

    # ADMIN_MENU_MESSAGE += "\n\n" + einfo + "<b>List of Venue Bookings to be Approved:</b>"
    # for i in range(len(list_pending_venues)):
    #     ADMIN_MENU_MESSAGE += "\n\n<b>VENUE ID: " + str(list_venueIDs[i]) + "</b>"
    #     ADMIN_MENU_MESSAGE += "\n\n" + str(list_pending_venues[i])
    #     ADMIN_MENU_MESSAGE += "\n\n" + "/approveVenue" + list_venueIDs[i] + " | " +  "/rejectVenue" + list_venueIDs[i] 
    
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

                LOGIN: [MessageHandler(Filters.text, login_verify),
                        CallbackQueryHandler(callback = start, pattern = '^(back)$')],

                VERIFY_LOGIN: [CallbackQueryHandler(callback = login, pattern = '^(login_fail)$'),
                                CallbackQueryHandler(callback = dashboard, pattern = '^(login_success)$')],

                FIRST_NAME: [MessageHandler(Filters.text, showtoken),
                            CallbackQueryHandler(callback = register, pattern = '^(register_back)$')],

                # LAST_NAME: [MessageHandler(Filters.text, showtoken),
                #             CallbackQueryHandler(callback = register, pattern = '^(back)$')],

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

                AFTER_MANAGE_EVENTS: [CallbackQueryHandler(callback = start_edit_event, pattern = '^[0-9]{4}$'),
                                        CallbackQueryHandler(callback = start_create_event, pattern = '^(create_event)$'),
                                        CallbackQueryHandler(callback = dashboard, pattern = '^(back)$')],
                
                AFTER_START_EDIT_EVENT: [CallbackQueryHandler(callback = cancel_date, pattern = '^(canceldate)'),
                                        CallbackQueryHandler(callback = rename_event, pattern = '^(rename_event)$'),
                                        CallbackQueryHandler(callback = edit_event_desc, pattern = '^(edit_desc)$'),
                                        CallbackQueryHandler(callback = book_venue, pattern = '^(book_venue)$'),
                                        CallbackQueryHandler(callback = request_publish_event, pattern = '^(request_publish)$'),
                                        CallbackQueryHandler(callback = manage_events, pattern = '^(back)$')],
                
                CREATE_NEW_EVENT: [MessageHandler(Filters.text, create_event_name),
                                    CallbackQueryHandler(callback = manage_events, pattern = '^(back)$')],

                CREATE_EVENT_DESC: [MessageHandler(Filters.text, final_create_event)],

                FINAL_CREATE_EVENT: [CallbackQueryHandler(callback = manage_events, pattern = '^(back_to_manage_events)$')],

                RENAME_EVENT: [MessageHandler(Filters.text, process_rename_event),
                                CallbackQueryHandler(callback = start_edit_event, pattern = '^[0-9]{4}$')],

                RENAME_EVENT_CONFIRM: [CallbackQueryHandler(callback = start_edit_event, pattern = '^[0-9]{4}$')],

                EDIT_EVENT_DESCRIPTION: [MessageHandler(Filters.text, process_event_description_edit),
                                        CallbackQueryHandler(callback = start_edit_event, pattern = '^[0-9]{4}$')],

                EDIT_EVENT_DESCRIPTION_CONFIRM: [CallbackQueryHandler(callback = start_edit_event, pattern = '^[0-9]{4}$')],

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

    published_events_list = DB().generate_all_approved_events()
    # create unique command for each registration of events:
    for i in range(len(published_events_list)):
        registercommandtext = 'registerForEvent' + str(published_events_list[i][0])
        dispatcher.add_handler(CommandHandler(command = registercommandtext, callback = confirm_event_registration))

    dispatcher.add_handler(CallbackQueryHandler(callback = calendar_handler, pattern = '^(get_calendar)$'))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()