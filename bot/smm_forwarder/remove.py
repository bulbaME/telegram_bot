from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from ..data import *
from ..misc import STEPS

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return
    
    groups_btn = []
    groups = list(data_sites_get().keys())
    for i in range(len(groups)):
        groups_btn.append([InlineKeyboardButton(groups[i], callback_data=f'{i + 1000}')])

    btn = InlineKeyboardButton('❌ Cancel', callback_data=STEPS.SMM_FORWARDER.LIST.SHOW_GROUP)
    groups_btn.append([btn])

    keyboard = InlineKeyboardMarkup(groups_btn)
    await context.bot.send_message(chat_id=chat_id, text='📃 Choose group to remove site(s)', reply_markup=keyboard)
    
    return STEPS.SMM_FORWARDER.LIST.SITES_DELETE

async def remove_select_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    g = int(update.callback_query.data) - 1000
    groups = list(data_sites_get().keys())

    btn = InlineKeyboardButton('❌ Cancel', callback_data=STEPS.SMM_FORWARDER.LIST.SHOW_GROUP)
    keyboard = InlineKeyboardMarkup([[btn]])

    context.user_data['current_group'] = groups[g]
    await context.bot.send_message(chat_id=chat_id, text=f'📃 List site(s) to remove from {groups[g]}', reply_markup=keyboard)

    return STEPS.SMM_FORWARDER.LIST.SITES_DELETE_SELECT

async def remove_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    text = update.message.text

    sites = [s.lower().strip() for s in text.split('\n')]

    for s in sites:
        data_sites_remove(context.user_data['current_group'], s)
    
    await context.bot.send_message(chat_id=chat_id, text=f'📃 {len(sites)} site(s) removed')

    return STEPS.SMM_FORWARDER.LIST.SHOW_GROUP
