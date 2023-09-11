from .forwarder_worker import site_process
from logs import print_site_log
from urllib.parse import urlparse
from multiprocessing import Pool
import os
import ctypes

MAX_TRIES = 2
MAX_SITES = 4

def send_ticket(url, subject, text, cred, n=None):
    i = 0

    while i < MAX_TRIES:
        try:
            site_process(url, cred, subject, text)
            break
        except BaseException as e:
            print_site_log(urlparse(url).netloc, e, err=True)

        i += 1

    if i < MAX_TRIES:
        return (n, 1)
    else:
        return (n, 2)

TICKET_PROC = {}

def send_tickets_concurr(urls: list, subject: str, text: str, cred, status_callback=None):

    i = 0
    while i < len(urls):
        with Pool(processes=os.cpu_count()) as pool:
            for _ in range(MAX_SITES):
                if i == len(urls):
                    break
                
                pool.apply_async(send_ticket, args=(urls[i], subject, text, cred, i), callback=status_callback)
                i += 1

            pool.close()
            pool.join()