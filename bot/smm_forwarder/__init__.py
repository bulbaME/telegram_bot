from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants, Message
from telegram.ext import ContextTypes
from ..data import *
from forwarder import send_tickets_concurr, TICKET_PROC
import asyncio
import time
from ..misc import STEPS
from forwarder.forwarder_worker import get_captcha_balance

async def forwarder_smm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    btn_list = InlineKeyboardButton('📃 List', callback_data=STEPS.SMM_FORWARDER.LIST.ENTRY)
    btn_ticket = InlineKeyboardButton('🎟 Ticket', callback_data=STEPS.SMM_FORWARDER.TICKET.ENTRY)
    btn_balance = InlineKeyboardButton('💳 2captcha balance', callback_data=STEPS.SMM_FORWARDER.BALANCE)

    keyboard = InlineKeyboardMarkup([[btn_list], [btn_ticket], [btn_balance]])

    await context.bot.send_message(chat_id=chat_id, text=f'🤖 SMM FORWARDER BOT PANEL', reply_markup=keyboard)

    return STEPS.MENU.SMM_FORWARDER


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    await context.bot.send_message(chat_id=chat_id, text=f'💳 Your 2captcha balance is {get_captcha_balance()}')

    return STEPS.MENU.SMM_FORWARDER

