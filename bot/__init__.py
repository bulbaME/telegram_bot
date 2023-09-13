import logging
import telegram
from telegram import Update, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
import yaml

from forwarder.forwarder_worker import get_captcha_balance

from .data import *
from .add import *
from .remove import *
from .ticket import *
from .auth import *
from .list import *

TOKEN = yaml.safe_load(open('credentials.yaml'))['tg']['token']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = data_users_get()
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_name in users.keys() or not users[user_name]['auth']:
        btn = InlineKeyboardButton('Authenticate', callback_data='2')
        keyboard = InlineKeyboardMarkup([[btn]])
        await context.bot.send_message(chat_id=chat_id, text="🖐 Hi, you should complete authorization to continue", reply_markup=keyboard)

        d = {
            'auth': False,
            'chat_id': update.effective_chat.id
        }

        data_users_set(user_name, d)

        return 2
    else:
        await context.bot.send_message(chat_id=chat_id, text="📃 You are authorized, try /help")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    await context.bot.send_message(chat_id=chat_id, text=f'💳 Your 2captcha balance is {get_captcha_balance()}')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return
    
    await context.bot.send_message(chat_id=chat_id, text='''
/add - add site to the list
/remove - remove site from the list
/list - list all site groups
/ticket - new ticket
/help - help command
/logout - logout
    ''')

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return
    
    users = data_users_get()
    user = users[user_name]
    user['auth'] = False

    data_users_set(user_name, user)

    await context.bot.delete_my_commands(telegram.BotCommandScopeChat(chat_id))

    btn = MenuButton(MenuButton.DEFAULT)
    await context.bot.set_chat_menu_button(chat_id=chat_id, menu_button=btn)
    await context.bot.send_message(chat_id=chat_id, text='🔴 Loged out successfully\n\n/start')

async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='❌ Addition canceled')

    return 11

async def cancel_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='❌ Removal canceled')

    return 14

async def cancel_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='❌ List canceled')

    return 21

def init():
    data_dir()
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    list_handler = CommandHandler('list', list_hndl)
    add_handler = CommandHandler('add', add)
    remove_handler = CommandHandler('remove', remove)
    ticket_handler = CommandHandler('ticket', new_ticket)
    help_handler = CommandHandler('help', help)
    logout_handler = CommandHandler('logout', logout)
    balance_handler = CommandHandler('balance', balance)

    auth_conversation = ConversationHandler(
        [start_handler],
        {
            2: [CallbackQueryHandler(auth, pattern=f'^2$')],
            3: [MessageHandler(filters.TEXT, passcode)],
            4: [start_handler]
        },
        [start_handler]
    )

    ticket_conversation = ConversationHandler(
        [ticket_handler],
        {
            5: [CallbackQueryHandler(conv_ticket_group, pattern='^([1-9][0-9])$')],
            6: [MessageHandler(filters.TEXT, conv_subject)],
            7: [MessageHandler(filters.TEXT, conv_message)],
            8: [CallbackQueryHandler(conv_send, pattern='^7$'), CallbackQueryHandler(conv_cancel, pattern='^8$')],
            9: [ticket_handler]
        },
        []
    )

    add_sites_convesation = ConversationHandler(
        [add_handler],
        {
            9: [CallbackQueryHandler(add_select_group, pattern='^([1-9][0-9])$')],
            10: [MessageHandler(filters.TEXT, add_conv)],
            11: [add_handler],
        },
        [CallbackQueryHandler(cancel_add, pattern='^0$')],
        block=True
    )

    remove_sites_convesation = ConversationHandler(
        [remove_handler],
        {
            12: [CallbackQueryHandler(remove_select_group, pattern='^([1-9][0-9])$')],
            13: [MessageHandler(filters.TEXT, remove_conv)],
            14: [remove_handler],
        },
        [CallbackQueryHandler(cancel_remove, pattern='^-1$')],
        block=True
    )

    list_sites_conversation = ConversationHandler(
        [list_handler],
        {
            15: [list_handler, CallbackQueryHandler(conv_list_add_group, pattern='^1$'), CallbackQueryHandler(conv_list_remove_group, pattern='^2$'), CallbackQueryHandler(conv_list_sites, pattern='^([1-9][0-9])$')],
            16: [list_handler, MessageHandler(filters.TEXT, conv_list_add_group_2)],
            17: [CallbackQueryHandler(conv_list_remove_group_2, pattern='^([1-9][0-9])$')],
            18: [list_handler, CallbackQueryHandler(conv_list_set_cred, pattern='^3$')],
            19: [MessageHandler(filters.TEXT, conv_list_set_cred_2)],
            20: [MessageHandler(filters.TEXT, conv_list_set_cred_conf)],
            21: [list_handler]
        },
        [CallbackQueryHandler(cancel_list, pattern='^-2$')],
        block=True
    )

    application.add_handler(auth_conversation)
    application.add_handler(ticket_conversation)
    application.add_handler(add_sites_convesation)
    application.add_handler(remove_sites_convesation)
    application.add_handler(list_sites_conversation)
    application.add_handler(help_handler)
    application.add_handler(logout_handler)
    application.add_handler(balance_handler)
    
        
    application.run_polling(timeout=60, pool_timeout=30)