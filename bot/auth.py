import telegram
from telegram import Update, BotCommand, MenuButton
from telegram.ext import ContextTypes
from .data import *
import yaml
from .misc import STEPS

PASSCODE = yaml.safe_load(open('credentials.yaml'))['tg']['pass_code']


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = data_users_get()
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if user_name in users.keys() and not users[user_name]['auth']:
        await context.bot.send_message(chat_id=chat_id, text='📟 Send the passcode')

    return STEPS.AUTH.PASSCODE

async def passcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = data_users_get()
    user_name = update.effective_user.username

    if update.message.text.strip() == PASSCODE:
        await context.bot.send_message(chat_id=chat_id, text='✅ You were successfully authorized')
        user = users[user_name]
        user['auth'] = True
        data_users_set(user_name, user)

        commands = [
            BotCommand('smm_forwarder', 'Smm Forwarder Bot'),
            BotCommand('search_panel', 'Search Panel'),
            BotCommand('mail_parser', 'Parse Mail On Websites'),
            BotCommand('mail_sender', 'Send emails'),
            BotCommand('logout', 'Logout'),
        ]
        await context.bot.set_my_commands(commands, telegram.BotCommandScopeChat(chat_id))

        btn = MenuButton(MenuButton.COMMANDS)
        await context.bot.set_chat_menu_button(chat_id=chat_id, menu_button=btn)

        return STEPS.AUTH.FINISH
    else:
        await context.bot.send_message(chat_id=chat_id, text='❌ Incorrect passcode, try again')
        return STEPS.AUTH.PASSCODE