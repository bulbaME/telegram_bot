from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha
import yaml
import requests
from urllib.parse import urlparse
from time import sleep
from logs import print_site_log

CRED = yaml.safe_load(open('credentials.yaml'))
MAX_WAITING_TIME = 5
CAPTCHA_SOLVER = TwoCaptcha(CRED['captcha']['token'], pollingInterval=5)

def get_captcha_balance() -> float:
    return CAPTCHA_SOLVER.balance()

def find_login_path(url) -> str:
    login_path = url
    src = requests.get(url)
    p = BeautifulSoup(src.text, 'html.parser')
    for l in p.find_all('a'):
        if l.get('href') == None: continue
        p = l.get('href').lower()

        if p.find('login') != -1:
            login_path = p
            break

        if p.find('sign') != -1 and p.find('in') != -1 and p.find('sign') < p.find('in'):
            login_path = p
            break

    login_path = urlparse(login_path).path
    if login_path == '/':
        login_path = ''

    return login_path

def find_tickets_path(driver: webdriver.Firefox, visited: set = set(), d = 0) -> str | None:
    tickets_path = None
    if d == 0:
        visited = set()

    if driver.current_url in visited:
        return None
    
    visited.add(driver.current_url)

    sleep(3)

    try:
        links = driver.find_elements(by=By.XPATH, value="//*[(text()[contains(., 'icket')]) or contains(text(), 'icket')]")
        for l in links:
            try:
                p = l.get_attribute('href').lower()
            
                if p.find('ticket') != -1:
                    tickets_path = p
                    break
            except BaseException:
                tickets_path = ''
                if l.is_displayed():
                    l.click()
                    break

        if tickets_path == None:
            for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'elp'))
            ):
                p = l.text.lower().strip()

                if p.find('help') != -1:
                    l.click()
                    tickets_path = find_tickets_path(driver, visited=visited, d=1)
                    if tickets_path != None:
                        break
            
        if tickets_path == None:
            for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'pport'))
            ):
                p = l.text.lower().strip()

                if p.find('support') != -1:
                    l.click()
                    tickets_path = find_tickets_path(driver, visited=visited, d=1)
                    if tickets_path != None:
                        break

        if tickets_path == None:
            for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'faq'))
            ):
                p = l.text.lower().strip()

                if p.find('faq') != -1:
                    l.click()
                    tickets_path = find_tickets_path(driver, visited=visited, d=1)
                    if tickets_path != None:
                        break

        return tickets_path
    except BaseException:
        driver.back()
        sleep(1)
        WebDriverWait(driver, MAX_WAITING_TIME).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))
        return None

def get_available_form(driver: webdriver.Firefox) -> WebElement | None:
    form: list[WebElement] = None

    try:
        form = WebDriverWait(driver, MAX_WAITING_TIME).until(
            expected_conditions.presence_of_all_elements_located((By.TAG_NAME, 'form'))
        )
    except BaseException as e:
        return None

    form = list(filter(lambda x: x.is_displayed(), form))
    form = list(filter(lambda x: x.get_attribute('method') != 'get', form))
    if len(form) == 0:
        return None

    return form[0]

def site_process(site_name: str, credentials, subject, text):
    if site_name.startswith('http'): 
        url = site_name
    else: 
        url = 'https://' + site_name

    driver_opt = Options()
    # driver_service = Service(executable_path='')
    driver_opt.headless = True
    driver_opt.add_argument("--window-size=800,800")
    driver_opt.page_load_strategy = 'eager'

    driver = webdriver.Firefox(options=driver_opt)

    try:
        login_path = url + find_login_path(url)
        driver.get(login_path)
        form = get_available_form(driver)

        sleep(1)
        captcha = None

        inputs = WebDriverWait(driver, MAX_WAITING_TIME).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        sleep(3)

        try:
            for e in driver.find_elements(by=By.TAG_NAME, value='iframe'):
                t = e.get_attribute('title')
                if t == None:
                    continue

                if t.lower().find('captcha') != -1:
                    captcha = e
                    break
        except BaseException:
            pass

        inputs: list[WebElement] = WebDriverWait(driver, MAX_WAITING_TIME).until(
            expected_conditions.presence_of_all_elements_located((By.TAG_NAME, 'input'))
        )

        inputs = list(filter(lambda e: e.is_displayed(), inputs))
        inputs[0].send_keys(credentials['username'])
        inputs[1].send_keys(credentials['password'])

        captcha_response = {}

        if captcha != None and captcha.is_displayed():
            e = driver.find_element(by=By.CLASS_NAME, value='g-recaptcha')
            k = e.get_attribute('data-sitekey')
            print_site_log(site_name, 'Captcha detected')

            if len(k) == 0:
                raise BaseException('Site recaptcha failed')

            try:
                captcha_response = CAPTCHA_SOLVER.recaptcha(k, driver.current_url)
                driver.execute_script(
                    f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_response["code"]}";'
                )
            except BaseException as e:
                raise BaseException('Site recaptcha failed')

        # old_url = driver.current_url
        form.submit()

        # if 'captchaId' in captcha_response.keys():
        #     if old_url == driver.current_url:
        #         CAPTCHA_SOLVER.report(captcha_response['captchaId'], False)
        #         raise BaseException('Captcha failed')
        #     else:
        #         CAPTCHA_SOLVER.report(captcha_response['captchaId'], True)
        #         print_site_log(site_name, 'Captcha solved')
        
        sleep(3)
        WebDriverWait(driver, MAX_WAITING_TIME).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))

        tickets = find_tickets_path(driver)
        if tickets != '':
            if tickets.startswith('/'):
                tickets = url + tickets

            if tickets == None:
                raise BaseException('Tickets page not found')
            else:
                print_site_log(site_name, 'Tickets page found')

            driver.get(tickets)
        sleep(3)

        buttons = driver.find_elements(by=By.XPATH, value="//button[contains(text(), 'icket')]")
        buttons.extend(driver.find_elements(by=By.XPATH, value="//summary[contains(text(), 'icket')]"))
        form = get_available_form(driver)
        if form == None:
            for b in buttons:
                if not b.is_displayed(): continue
                b.click()
                sleep(1)

                form = get_available_form(driver)
                if form != None: break

        selects = form.find_elements(by=By.TAG_NAME, value='select')
        selects = list(filter(lambda e: e.is_displayed(), selects))

        if len(selects) > 0:
            select = selects[0]
            WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.element_to_be_clickable(select)
            )
            
            select.click()
            children = select.find_elements(by=By.XPATH, value="*[contains(text(), 'ther')]")

            if len(children) == 0:
                children = select.find_elements(by=By.XPATH, value="*")
                children[-1].click()
            else:
                children[0].click()
        
        inputs = form.find_elements(by=By.TAG_NAME, value='input')
        inputs = list(filter(lambda e: e.is_displayed(), inputs))

        texts = form.find_elements(by=By.TAG_NAME, value='textarea')
        texts = list(filter(lambda e: e.is_displayed(), texts))

        if len(inputs) == 0:
            texts[0].clear()
            texts[0].send_keys(f'{subject}\n\n{text}')
        else:
            inputs[0].clear()
            inputs[0].send_keys(subject)
            texts[0].clear()
            texts[0].send_keys(text)

        # form.screenshot(f'{site_name}.png')
        form.submit()
        buttons = form.find_elements(by=By.XPATH, value="//button[contains(text(), 'icket')]")
        buttons.extend(form.find_elements(by=By.XPATH, value="//*[contains(text(), 'ubmit')]"))
        buttons = list(filter(lambda x: x.is_displayed(), buttons))

        if len(buttons) > 0:
            buttons[-1].click()

        sleep(3)
        print_site_log(site_name, 'Ticket sent successfully')

        driver.quit()
    except BaseException as e:
        driver.quit()
        raise e
