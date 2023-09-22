import mail_parser
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants, Message
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from .misc import STEPS
from multiprocessing import Pool
import os

async def mail_parser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    btn_query = InlineKeyboardButton('🔗 START PARSING', callback_data=STEPS.MAIL_PARSER.PROCEED)

    keyboard = InlineKeyboardMarkup([[btn_query]])

    await context.bot.send_message(chat_id=chat_id, text=f'✉ MAIL PARSER\nParse websites for contact e-mail', reply_markup=keyboard)

    return STEPS.MAIL_PARSER.ENTRY

async def mail_parse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await context.bot.send_message(chat_id=chat_id, text=f'Send website list, one website per line')

    return STEPS.MAIL_PARSER.PROCEED

async def proceed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    sites = update.effective_message.text.split('\n')
    sites = [s.strip() for s in sites]

    await context.bot.send_message(chat_id=chat_id, text=f'⚙ Parsing began, result will be sent to you as a file')

    ls = []

    with Pool(os.cpu_count()) as pool:
        for s in sites:
            pool.apply_async(mail_parser.get_contact_mail, (s, ), callback=lambda x: ls.append(x) if x != None else 0)
        
        pool.close()
        pool.join()

    s = '\n'.join(ls) + ' '
    fw = open('data/tmp', 'w')
    fw.write(s)
    fw.close()

    await context.bot.send_document(chat_id, open('data/tmp'), filename='e-mails.txt')

    return STEPS.MAIL_PARSER.ENTRY