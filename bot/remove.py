from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .data import *

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await context.bot.send_message(chat_id=chat_id, text='📃 Choose group to remove site(s)', reply_markup=keyboard)
    
    return 12

async def remove_select_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    g = int(update.callback_query.data) - 10
    groups = list(data_sites_get().keys())

    btn = InlineKeyboardButton('❌ Cancel', callback_data='-1')
    keyboard = InlineKeyboardMarkup([[btn]])

    context.user_data['current_group'] = groups[g]
    await context.bot.send_message(chat_id=chat_id, text=f'📃 List site(s) to remove from {groups[g]}', reply_markup=keyboard)

    return 13

async def remove_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    text = update.message.text

    sites = [s.lower().strip() for s in text.split('\n')]

    for s in sites:
        data_sites_remove(context.user_data['current_group'], s)
    
    await context.bot.send_message(chat_id=chat_id, text=f'📃 {len(sites)} site(s) removed')

    return 14
