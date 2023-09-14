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
MAX_WAITING_TIME = 10
CAPTCHA_SOLVER = TwoCaptcha(CRED['captcha']['token'], pollingInterval=5)

def get_captcha_balance() -> float:
    return CAPTCHA_SOLVER.balance()

def find_login_path(url) -> str:
    login_path = url
    src = requests.get(url)
    p = BeautifulSoup(src.text, 'html.parser')
    for l in p.find_all('a'):
        p = l.get('href').lower()

        if p.find('login') != -1:
            login_path = p
            break

        if p.find('sign') != -1 and p.find('in') != -1 and p.find('sign') < p.find('in'):
            login_path = p
            break

    login_path = urlparse(login_path).path

    return login_path

def find_tickets_path(driver: webdriver.Firefox, visited: set = set()) -> str | None:
    tickets_path = None

    sleep(3)
    WebDriverWait(driver, MAX_WAITING_TIME).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))
    if driver.current_url in visited:
        return None
    
    visited.add(driver.current_url)

    try:
        for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
            expected_conditions.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        ):
            p = l.get_attribute('href').lower()

            if p.find('ticket') != -1:
                tickets_path = p
                break

        if tickets_path == None:
            for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'elp'))
            ):
                p = l.text.lower().strip()

                if p.find('help') != -1:
                    l.click()
                    tickets_path = find_tickets_path(driver, visited=visited)
                    if tickets_path != None:
                        break
            
        if tickets_path == None:
            for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'pport'))
            ):
                p = l.text.lower().strip()

                if p.find('support') != -1:
                    l.click()
                    tickets_path = find_tickets_path(driver, visited=visited)
                    if tickets_path != None:
                        break

        if tickets_path == None:
            for l in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'faq'))
            ):
                p = l.text.lower().strip()

                if p.find('faq') != -1:
                    l.click()
                    tickets_path = find_tickets_path(driver, visited=visited)
                    if tickets_path != None:
                        break

        return tickets_path
    except BaseException:
        driver.back()
        sleep(3)
        WebDriverWait(driver, MAX_WAITING_TIME).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))
        return None

def get_available_form(driver: webdriver.Firefox) -> WebElement | None:
    form = None
    site_name = urlparse(driver.current_url).netloc

    try:
        form = WebDriverWait(driver, MAX_WAITING_TIME).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'form'))
        )
    except BaseException as e:
        driver.close()
        print_site_log(site_name, 'Couldn\'t load the page', err=True)

    return form

def site_process(site_name, credentials, subject, text):
    url = 'https://' + site_name

    driver_opt = Options()
    driver_service = Service(executable_path='./geckodriver.exe')
    # driver_opt.headless = True
    driver_opt.add_argument("--window-size=800,800")
    driver_opt.page_load_strategy = 'eager'

    driver = webdriver.Firefox(options=driver_opt, service=driver_service)

    try:
        login_path = url + find_login_path(url)
        driver.get(login_path)
        form = get_available_form(driver)

        sleep(3)
        captcha = None

        try:
            for e in WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.presence_of_all_elements_located((By.TAG_NAME, 'iframe'))
            ):
                t = e.get_attribute('title')
                if t == None:
                    continue

                if t.lower().find('captcha') != -1:
                    captcha = e
                    break
        except BaseException:
            pass

        inputs = WebDriverWait(driver, MAX_WAITING_TIME).until(
            expected_conditions.presence_of_all_elements_located((By.TAG_NAME, 'input'))
        )

        inputs = list(filter(lambda e: e.is_displayed(), inputs))
        inputs[0].clear()
        inputs[0].click()
        inputs[0].send_keys(credentials['username'])
        inputs[1].clear()
        inputs[1].click()
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

        old_url = driver.current_url
        form.submit()
        sleep(3)

        # if 'captchaId' in captcha_response.keys():
        #     if old_url == driver.current_url:
        #         CAPTCHA_SOLVER.report(captcha_response['captchaId'], False)
        #         raise BaseException('Captcha failed')
        #     else:
        #         CAPTCHA_SOLVER.report(captcha_response['captchaId'], True)
        #         print_site_log(site_name, 'Captcha solved')

        tickets = find_tickets_path(driver)
        if tickets == None:
            raise BaseException('Tickets page not found')
        else:
            print_site_log(site_name, 'Tickets page found')


        driver.get(tickets)
        sleep(3)
        form = get_available_form(driver)

        selects = form.find_elements(by=By.TAG_NAME, value='select')
        selects = list(filter(lambda e: e.is_displayed(), selects))

        if len(selects) > 0:
            WebDriverWait(driver, MAX_WAITING_TIME).until(
                expected_conditions.element_to_be_clickable((By.TAG_NAME, 'select'))
            )
            select = selects[0]
            select.click()
            children = select.find_elements(By.XPATH, '*')
            if len(children) > 0:
                children[-1].click()
        
        inputs = form.find_elements(by=By.TAG_NAME, value='input')
        inputs = list(filter(lambda e: e.is_displayed(), inputs))

        texts = form.find_elements(by=By.TAG_NAME, value='textarea')
        texts = list(filter(lambda e: e.is_displayed(), texts))

        if len(inputs) == 0:
            texts[0].clear()
            texts[0].send_keys(f'{subject}:\n\n{text}')
        else:
            inputs[0].clear()
            inputs[0].send_keys(subject)
            texts[0].clear()
            texts[0].send_keys(text)

        form.screenshot(f'{site_name}.png')
        form.submit()
        sleep(1)
        print_site_log(site_name, 'Ticket sent successfully')

        driver.quit()
    except BaseException as e:
        driver.quit()
        raise e
