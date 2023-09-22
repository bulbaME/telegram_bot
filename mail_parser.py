from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup, PageElement
from time import sleep
import random

MAIL_PREFIX = [
    'support',
    'contact',
    'business',
    'help',
    'admin'
]

MAX_WAIT_TIME = 15

def get_contact_mail(url: str, visited: set = set(), driver = None, sub=False) -> str | None:
    if url in visited:
        return None
    
    visited.add(url)

    if driver == None:
        driver_opt = Options()
        driver_service = Service(executable_path='./geckodriver.exe')
        driver_opt.headless = True
        driver_opt.add_argument("--window-size=800,800")
        driver_opt.page_load_strategy = 'eager'

        driver = webdriver.Firefox(options=driver_opt, service=driver_service)

    mail = None

    try:
        driver.get(url)

        WebDriverWait(driver, MAX_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        mails = driver.find_elements(by=By.XPATH, value="//*[text()[contains(., '@')]]")

        for m in mails:
            text = m.text.lower()

            for pr in MAIL_PREFIX:
                i = text.find(pr) 
                if i == -1: continue

                s = text[i:]
                s = s.split()[0]

                mail = s
                break

        if mail == None and len(mails) > 0:
            mails = mails[0].text.lower()
            mails = mails.split()
            for m in mails:
                if m.find('@') != None:
                    mail = m
                    break

        if mail == None and not sub: 
            links = driver.find_elements(by=By.TAG_NAME, value='a')
            
            for t in links:
                link = None
                try:
                    link = t.get_attribute('href').lower()
                except BaseException:
                    continue

                if link.find('contact') == -1: continue
                
                contact_url = ''

                if link.startswith('/'):
                    contact_url = url + link
                elif link.startswith(url):
                    contact_url = link
                else:
                    contact_url = url + '/' + link

                mail = get_contact_mail(contact_url, visited=visited, driver=driver, sub=True)
                if mail != None: break
                driver.back()

    except BaseException as e:
        pass

    if not sub: driver.quit()

    return mail