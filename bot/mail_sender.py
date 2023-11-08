import mail_sender
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants, Message
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from .misc import STEPS

async def email_sender_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name):
        return

    btn = InlineKeyboardButton('✉ SEND EMAILS', callback_data=STEPS.MAIL_SENDER.MAILS)
    keyboard = InlineKeyboardMarkup([[btn]])

    await context.bot.send_message(chat_id=chat_id, text=f'✉ EMAIL SENDER\nSend messages to indicated emails', reply_markup=keyboard)

    return STEPS.MAIL_SENDER.ENTRY

async def set_mails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    await context.bot.send_message(chat_id=chat_id, text=f'Send email list (1 email per line)')

    return STEPS.MAIL_SENDER.MAILS

async def set_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username
    
    emails = [v.strip() for v in update.effective_message.text.split('\n')]
    context.user_data['mails'] = emails

    await context.bot.send_message(chat_id=chat_id, text=f'Send email subject')

    return STEPS.MAIL_SENDER.SUBJECT

async def set_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    subject = update.effective_message.text
    context.user_data['subject'] = subject

    await context.bot.send_message(chat_id=chat_id, text=f'Send html file')

    return STEPS.MAIL_SENDER.CONTENT

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    file_id = update.effective_message.document.file_id

    file = await context.bot.get_file(file_id)
    await file.download_to_drive('data/tmp')
    file = open('data/tmp', encoding='utf-8')
    content = file.read()
    file.close()

    context.user_data['content'] = content

    btn1 = InlineKeyboardButton('✅ Confirm', callback_data=STEPS.MAIL_SENDER.PROCEED)
    btn2 = InlineKeyboardButton('❌ Cancel', callback_data=STEPS.MAIL_SENDER.ENTRY)

    keyboard = InlineKeyboardMarkup([[btn1], [btn2]])

    await context.bot.send_message(chat_id=chat_id, text=f'📨 Confirm sending mails', reply_markup=keyboard)

    return STEPS.MAIL_SENDER.PROCEED

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    mails = context.user_data['mails']
    subject = context.user_data['subject']
    content = context.user_data['content']

    status = '\n'.join([f'🟡 {v}' for v in mails])

    message = await context.bot.send_message(chat_id, status)

    try:
        res = mail_sender.send_mail(mails, subject, content)
    except BaseException:
        res = {v : False for v in mails}

    status = '\n'.join([f'{"✅" if v else "❌"} {k}' for (k, v) in res.items()])

    await message.edit_text(status)

    return STEPS.MAIL_SENDER.ENTRY