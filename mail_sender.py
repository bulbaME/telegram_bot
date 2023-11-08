from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import yaml
import time

CRED = yaml.safe_load(open('credentials.yaml'))['mail_sender']

EMAIL = CRED['mail']
PASSWORD = CRED['password']
SERVER = 'smtp.office365.com'
PORT = 587
MAX_WAIT_TIME = 60

def send_mail(recievers: list[str], subject, content):
    smtp = smtplib.SMTP(host = SERVER, port = PORT)
    smtp.starttls()
    smtp.login(EMAIL, PASSWORD)

    mime_content = MIMEText(content, 'html')
    message = MIMEMultipart('alternative')
    message['From'] = 'smmpanel'
    message['Subject'] = subject
    message.attach(mime_content)

    result = { v: True for v in recievers }

    resp = smtp.sendmail(EMAIL, recievers, message.as_string())

    for k in resp.keys():
        result[k] = False

    return result