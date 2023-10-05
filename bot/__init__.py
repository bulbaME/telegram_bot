import logging
import telegram
from telegram import Update, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
import yaml

from .data import *
from .auth import *
from .misc import STEPS
from . import smm_forwarder
from .smm_forwarder import list as smm_frwd_list
from .smm_forwarder import ticket as smm_frwd_ticket
from .smm_forwarder import remove as smm_frwd_remove
from .smm_forwarder import add as smm_frwd_add

from . import web_search
from . import mail_parser

TOKEN = yaml.safe_load(open('credentials.yaml'))['tg']['token']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = data_users_get()
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_name in users.keys() or not users[user_name]['auth']:
        btn = InlineKeyboardButton('Authenticate', callback_data=STEPS.AUTH.AUTH)
        keyboard = InlineKeyboardMarkup([[btn]])
        await context.bot.send_message(chat_id=chat_id, text="🖐 Hi, you should complete authorization to continue", reply_markup=keyboard)

        d = {
            'auth': False,
            'chat_id': update.effective_chat.id
        }

        data_users_set(user_name, d)

        return STEPS.AUTH.AUTH
    else:
        await context.bot.send_message(chat_id=chat_id, text="📃 You are authorized, try /help")
        return STEPS.AUTH.FINISH


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

def init():
    data_dir()
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    logout_handler = CommandHandler('logout', logout)
    forwarder_smm_handler = CommandHandler('smm_forwarder', smm_forwarder.forwarder_smm)
    web_search_handler = CommandHandler('search_panel', web_search.web_search_menu)
    mail_parser_handler = CommandHandler('mail_parser', mail_parser.mail_parser_command)

    auth_conversation = ConversationHandler(
        [start_handler],
        {
            STEPS.AUTH.AUTH: [CallbackQueryHandler(auth, pattern=f'^{STEPS.AUTH.AUTH}$')],
            STEPS.AUTH.PASSCODE: [MessageHandler(filters.TEXT, passcode)],
            STEPS.AUTH.FINISH: [start_handler]
        },
        []
    )

    forwarder_smm_conversation = ConversationHandler(
        [forwarder_smm_handler],
        {
            STEPS.MENU.SMM_FORWARDER: [
                CallbackQueryHandler(smm_frwd_list.list_hndl, pattern=f'^{STEPS.SMM_FORWARDER.LIST.ENTRY}$'),
                CallbackQueryHandler(smm_frwd_ticket.new_ticket, pattern=f'^{STEPS.SMM_FORWARDER.TICKET.ENTRY}$'),
                CallbackQueryHandler(smm_forwarder.balance, pattern=f'^{STEPS.SMM_FORWARDER.BALANCE}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.ENTRY: [
                forwarder_smm_handler,
                CallbackQueryHandler(smm_frwd_list.conv_list_add_group, pattern=f'^{STEPS.SMM_FORWARDER.LIST.ADD_GROUP}$'),
                CallbackQueryHandler(smm_frwd_list.conv_list_remove_group, pattern=f'^{STEPS.SMM_FORWARDER.LIST.DEL_GROUP}$'),
                CallbackQueryHandler(smm_frwd_add.add, pattern=f'^{STEPS.SMM_FORWARDER.LIST.SITES_ADD}$'),
                CallbackQueryHandler(smm_frwd_remove.remove, pattern=f'^{STEPS.SMM_FORWARDER.LIST.SITES_DELETE}$'),
                CallbackQueryHandler(smm_frwd_list.conv_list_sites, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
            ],
            STEPS.SMM_FORWARDER.LIST.ADD_GROUP_SELECT: [
                MessageHandler(filters.TEXT, smm_frwd_list.conv_list_add_group_2),
                CallbackQueryHandler(smm_forwarder.forwarder_smm, pattern=f'^{STEPS.SMM_FORWARDER.LIST.ENTRY}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.DEL_GROUP_SELECT: [
                CallbackQueryHandler(smm_frwd_list.conv_list_remove_group_2, pattern=f'^(?:200[0-9]|20[1-9][0-9]|2[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(smm_forwarder.forwarder_smm, pattern=f'^{STEPS.SMM_FORWARDER.LIST.ENTRY}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.SHOW_GROUP: [
                forwarder_smm_handler,
                CallbackQueryHandler(smm_frwd_list.conv_list_set_cred, pattern=f'^{STEPS.SMM_FORWARDER.LIST.GROUP_SET_CRED}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.CRED_USERNAME: [
                MessageHandler(filters.TEXT, smm_frwd_list.conv_list_set_cred_2),
            ],
            STEPS.SMM_FORWARDER.LIST.CRED_PASSWORD: [
                MessageHandler(filters.TEXT, smm_frwd_list.conv_list_set_cred_conf),
            ],
            STEPS.SMM_FORWARDER.LIST.SITES_ADD: [
                CallbackQueryHandler(smm_frwd_add.add_select_group, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(smm_frwd_list.list_hndl, pattern=f'^{STEPS.SMM_FORWARDER.LIST.SHOW_GROUP}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.SITES_ADD_SELECT: [
                MessageHandler(filters.TEXT, smm_frwd_add.add_conv),
                CallbackQueryHandler(smm_frwd_list.list_hndl, pattern=f'^{STEPS.SMM_FORWARDER.LIST.SHOW_GROUP}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.SITES_DELETE: [
                CallbackQueryHandler(smm_frwd_remove.remove_select_group, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(smm_frwd_list.list_hndl, pattern=f'^{STEPS.SMM_FORWARDER.LIST.SHOW_GROUP}$'),
            ],
            STEPS.SMM_FORWARDER.LIST.SITES_DELETE_SELECT: [
                MessageHandler(filters.TEXT, smm_frwd_remove.remove_conv),
                CallbackQueryHandler(smm_frwd_list.list_hndl, pattern=f'^{STEPS.SMM_FORWARDER.LIST.SHOW_GROUP}$'),
            ],
            STEPS.SMM_FORWARDER.TICKET.GROUP: [
                CallbackQueryHandler(smm_frwd_ticket.conv_ticket_group, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(smm_forwarder.forwarder_smm, pattern=f'^{STEPS.MENU.SMM_FORWARDER}$'),
            ],
            STEPS.SMM_FORWARDER.TICKET.SUBJECT: [
                MessageHandler(filters.TEXT, smm_frwd_ticket.conv_subject),
                CallbackQueryHandler(smm_forwarder.forwarder_smm, pattern=f'^{STEPS.MENU.SMM_FORWARDER}$'),
            ],
            STEPS.SMM_FORWARDER.TICKET.TEXT: [
                MessageHandler(filters.TEXT, smm_frwd_ticket.conv_message),
                CallbackQueryHandler(smm_forwarder.forwarder_smm, pattern=f'^{STEPS.MENU.SMM_FORWARDER}$'),
            ],
            STEPS.SMM_FORWARDER.TICKET.CONFIRM: [
                CallbackQueryHandler(smm_frwd_ticket.conv_send, pattern=f'^{STEPS.SMM_FORWARDER.TICKET.CONFIRM}$'),
                CallbackQueryHandler(smm_forwarder.forwarder_smm, pattern=f'^{STEPS.MENU.SMM_FORWARDER}$'),
            ]
        },
        [],
        allow_reentry=True
    )

    web_search_conversation = ConversationHandler(
        [web_search_handler],
        {
            STEPS.WEB_SEARCH.ENTRY: [
                CallbackQueryHandler(web_search.ask_country, pattern=f'^{STEPS.WEB_SEARCH.ENTRY}$'),
            ],
            STEPS.WEB_SEARCH.COUNTRY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, web_search.ask_query),
            ],
            STEPS.WEB_SEARCH.QUERY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, web_search.ask_pages),
            ],
            STEPS.WEB_SEARCH.PAGES: [
                CallbackQueryHandler(web_search.proceed_search, pattern=f'^250[0-9]$'),
            ]
        },
        [],
        allow_reentry=True
    )

    mail_parser_conversation = ConversationHandler(
        [mail_parser_handler],
        {
            STEPS.MAIL_PARSER.ENTRY: [
                CallbackQueryHandler(mail_parser.mail_parse_command, pattern=f'^{STEPS.MAIL_PARSER.PROCEED}$'),
            ],
            STEPS.MAIL_PARSER.PROCEED: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, mail_parser.proceed_command),
            ]
        },
        [],
        allow_reentry=True
    )

    application.add_handler(auth_conversation)
    application.add_handler(forwarder_smm_conversation)
    application.add_handler(web_search_conversation)
    application.add_handler(mail_parser_conversation)
    application.add_handler(logout_handler)
        
    application.run_polling(timeout=60, pool_timeout=30)
