from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from ..data import *
from bot.misc import STEPS

async def list_hndl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return
    
    groups = list(data_sites_get().keys())
    groups_btn = []

    for i in range(len(groups)):
        groups_btn.append([InlineKeyboardButton(groups[i], callback_data=f'{i+1000}')])

    btn_add_g = InlineKeyboardButton('➕ Group', callback_data=STEPS.SMM_FORWARDER.LIST.ADD_GROUP)
    btn_remove_g = InlineKeyboardButton('➖ Group', callback_data=STEPS.SMM_FORWARDER.LIST.DEL_GROUP)
    btn_add = InlineKeyboardButton('➕ Sites', callback_data=STEPS.SMM_FORWARDER.LIST.SITES_ADD)
    btn_del = InlineKeyboardButton('➖ Sites', callback_data=STEPS.SMM_FORWARDER.LIST.SITES_DELETE)
    groups_btn.append([btn_add_g, btn_remove_g])
    groups_btn.append([btn_add, btn_del])

    keyboard = InlineKeyboardMarkup(groups_btn)
    msg = '📃 Site groups\n'
    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard)

    return STEPS.SMM_FORWARDER.LIST.ENTRY

async def conv_list_sites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    g = int(update.callback_query.data) - 1000
    groups_d = data_sites_get()
    groups = list(groups_d.keys())
    group = groups_d[groups[g]]
    context.user_data['current_group'] = groups[g]

    sites = '\n'.join(group['list'])
    
    btn = InlineKeyboardButton('Set login data', callback_data=STEPS.SMM_FORWARDER.LIST.GROUP_SET_CRED)
    keyboard = InlineKeyboardMarkup([[btn]])
    await context.bot.send_message(chat_id=chat_id, text=f'📃 {groups[g]} sites\n{sites}', reply_markup=keyboard)

    return STEPS.SMM_FORWARDER.LIST.SHOW_GROUP

async def conv_list_set_cred(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    group_name = context.user_data['current_group']

    await context.bot.send_message(chat_id=chat_id, text=f'📟 {group_name} username:')
    
    return STEPS.SMM_FORWARDER.LIST.CRED_USERNAME

async def conv_list_set_cred_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    group_name = context.user_data['current_group']
    msg = update.message.text.strip()
    context.user_data['username'] = msg

    await context.bot.send_message(chat_id=chat_id, text=f'📟 {group_name} password:')
    
    return STEPS.SMM_FORWARDER.LIST.CRED_PASSWORD

async def conv_list_set_cred_conf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    group_name = context.user_data['current_group']
    msg = update.message.text.strip()
    context.user_data['password'] = msg

    groups = data_sites_get()
    groups[group_name]['cred']['username'] = context.user_data['username']
    groups[group_name]['cred']['password'] = context.user_data['password']
    data_sites_set(groups)

    await context.bot.send_message(chat_id=chat_id, text=f'📟 {group_name} new credentials:\nusername: {context.user_data["username"]}\npassword: {context.user_data["password"]}')
    
    return STEPS.SMM_FORWARDER.LIST.ENTRY

async def conv_list_add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    
    btn = InlineKeyboardButton('❌ Cancel', callback_data=STEPS.SMM_FORWARDER.LIST.ENTRY)
    keyboard = InlineKeyboardMarkup([[btn]])

    await context.bot.send_message(chat_id=chat_id, text='📃 Name for new group:', reply_markup=keyboard)

    return STEPS.SMM_FORWARDER.LIST.ADD_GROUP_SELECT

async def conv_list_add_group_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    g = update.message.text.split('\n')[0].strip()

    data_sites_add_group(g)

    await context.bot.send_message(chat_id=chat_id, text=f'📃 Group {g} has been added')
    
    return STEPS.SMM_FORWARDER.LIST.ENTRY

async def conv_list_remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    groups = list(data_sites_get().keys())
    groups_btn = []

    for i in range(len(groups)):
        groups_btn.append([InlineKeyboardButton(groups[i], callback_data=f'{i+2000}')])

    btn = InlineKeyboardButton('❌ Cancel', callback_data=STEPS.SMM_FORWARDER.LIST.ENTRY)
    groups_btn.append([btn])

    keyboard = InlineKeyboardMarkup(groups_btn)
    await context.bot.send_message(chat_id=chat_id, text='📃 Select group to remove', reply_markup=keyboard)
    
    return STEPS.SMM_FORWARDER.LIST.DEL_GROUP_SELECT

async def conv_list_remove_group_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    g = int(update.callback_query.data) - 2000
    groups = list(data_sites_get().keys())

    data_sites_remove_group(groups[g])
    await context.bot.send_message(chat_id=chat_id, text=f'📃 Group {groups[g]} has been removed')
    
    return STEPS.SMM_FORWARDER.LIST.ENTRY

