from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants, Message
from telegram.ext import ContextTypes
from .data import *
from forwarder import send_tickets_concurr, TICKET_PROC
import asyncio
import time

async def new_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    groups_btn = []
    groups = list(data_sites_get().keys())
    for i in range(len(groups)):
        groups_btn.append([InlineKeyboardButton(groups[i], callback_data=f'{i + 10}')])

    btn = InlineKeyboardButton('❌ Cancel', callback_data='-1')
    groups_btn.append([btn])

    keyboard = InlineKeyboardMarkup(groups_btn)

    await context.bot.send_message(chat_id=chat_id, text='🎟 Select group', reply_markup=keyboard)
    
    return 5

async def conv_ticket_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    g = int(update.callback_query.data) - 10
    groups = list(data_sites_get().keys())
    context.user_data['current_group'] = groups[g]

    await context.bot.send_message(chat_id=chat_id, text='📃 Ticket subject: ')
    
    return 6

async def conv_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    context.user_data['subject'] = text

    await context.bot.send_message(chat_id=chat_id, text='📃 Ticket message: ')

    return 7

async def conv_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    context.user_data['text'] = text

    btn1 = InlineKeyboardButton('✅ Confirm', callback_data='7')
    btn2 = InlineKeyboardButton('❌ Cancel', callback_data='8')
    keyboard = InlineKeyboardMarkup([[btn1], [btn2]])
    await context.bot.send_message(chat_id=chat_id, text=f'🎟 Your ticket to {context.user_data["current_group"]}\n\n*{context.user_data["subject"]}*\n{context.user_data["text"]}', reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN_V2)
    
    return 8

async def update_status(status: list, sites: list):
    s = ''

    for i in range(len(status)):
        e = '🟡'

        if status[i] == 1:
            e = '✅'
        elif status[i] == 2:
            e = '❌'

        s += f'{e} {sites[i]}\n'

    while TICKET_PROC['last_edit']:
        time.sleep(0.1)

    TICKET_PROC['last_edit'] = True
    TICKET_PROC['message'] = await TICKET_PROC['message'].edit_text(s)
    TICKET_PROC['last_edit'] = False


async def conv_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=f'🎟 Sending your ticket...')
    TICKET_PROC['message'] = await context.bot.send_message(chat_id=chat_id, text='📃', disable_web_page_preview=False)
    TICKET_PROC['last_edit'] = False

    group = data_sites_get()[context.user_data['current_group']]
    sites = group['list']
    TICKET_PROC['status'] = [0 for _ in range(len(sites))]
    
    def update_callback(s):
        TICKET_PROC['status'][s[0]] = s[1]
        # try:
        #     asyncio.run(update_status(TICKET_PROC['status'], sites))
        # except BaseException as e:
        #     print(e)

    await update_status(TICKET_PROC['status'], sites)

    subject = context.user_data['subject']
    text = context.user_data['text']
    send_tickets_concurr(sites, subject, text, group['cred'], status_callback=update_callback)

    await update_status(TICKET_PROC['status'], sites)

    return 9

async def conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await context.bot.send_message(chat_id=chat_id, text=f'🎟 Ticket canceled')

    return 9