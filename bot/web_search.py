import web_search
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants, Message
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from .misc import STEPS

async def web_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    btn_query = InlineKeyboardButton('🔎 ENTER QUERY', callback_data=STEPS.WEB_SEARCH.ENTRY)

    keyboard = InlineKeyboardMarkup([[btn_query]])

    await context.bot.send_message(chat_id=chat_id, text=f'🔎 SEARCH PANEL\nWith country and query you provide, bot will search internet for websites', reply_markup=keyboard)

    return STEPS.WEB_SEARCH.ENTRY

async def ask_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    await context.bot.send_message(chat_id, f'Enter country name')

    return STEPS.WEB_SEARCH.COUNTRY


async def ask_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    code = update.message.text.lower().strip()
    code = web_search.get_country_code_similar(code)

    if code == None:
        await context.bot.send_message(chat_id, f'Couldn\'t find country by name, try again 🚫')

        return STEPS.WEB_SEARCH.ENTRY
    
    context.user_data['country_code'] = code

    name = web_search.find_by_code(code)
    await context.bot.send_message(chat_id, f'You choose {name}\nSend your search query')

    return STEPS.WEB_SEARCH.QUERY

        

async def ask_pages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    query = update.message.text.lower().strip()

    context.user_data['query'] = query

    btns = [
        [InlineKeyboardButton('1', callback_data=2500)],
        [InlineKeyboardButton('3', callback_data=2501)],
        [InlineKeyboardButton('5', callback_data=2502)],
        [InlineKeyboardButton('10', callback_data=2503)],
        [InlineKeyboardButton('25', callback_data=2504)],
    ]

    keyboard = InlineKeyboardMarkup(btns)

    await context.bot.send_message(chat_id, f'Country code - {context.user_data["country_code"]}\nSearch query - {query}\n\n Choose number of pages to retrieve (each page - 100 sites)', reply_markup=keyboard)

    return STEPS.WEB_SEARCH.PAGES

async def proceed_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    query = update.callback_query.data

    pages = 1
    if query == '2501':
        pages = 3
    elif query == '2502':
        pages = 5
    elif query == '2503':
        pages = 10
    elif query == '2504':
        pages = 25

    msg = await context.bot.send_message(chat_id, f'Parsing began... 🔗 <code>[0/{pages}]</code>', parse_mode=ParseMode.HTML)

    l = []
    for i in range(pages):
        l.extend(web_search.get_sites(context.user_data['country_code'], context.user_data['query'], i+1))

        msg = await msg.edit_text(f'Parsing began... 🔗 <code>[{i+1}/{pages}]</code>', parse_mode=ParseMode.HTML)
    
    l = list(set(l))

    f = open('data/tmp', 'w')
    f.write('\n'.join(l))    
    f.close()

    await context.bot.send_document(chat_id, open('data/tmp'), filename='sites.txt')

    return STEPS.WEB_SEARCH.ENTRY
