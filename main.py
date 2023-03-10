import requests
import time
import signal
import sys
import os
import hashlib
from urllib3.exceptions import InsecureRequestWarning
import csv

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


sites = [
    'https://nginx.local.akeb.ru/',
    'https://pve.local.akeb.ru/',
    'https://portainer.local.akeb.ru/',

    'https://akeb.ru/',
    'https://home.akeb.ru/',
    'https://books.akeb.ru/',
    'https://drive.akeb.ru/',
    # 'https://grafana.akeb.ru/',
    'https://keys.akeb.ru/',
    'https://numbers.akeb.ru/',
    'https://photo.akeb.ru/',
    'https://smart.akeb.ru/',
    'https://torrent.akeb.ru/',
    'https://wifi.akeb.ru/',

    'https://mbezhanova.ru/',
    # 'https://shop.mbezhanova.ru/',

    'https://ats.my.games/',
]

caches = {}


def telegram_bot_send_text(bot_message):
    bot_token = '309690176:AAG3eLnw2uLUyojkwE_fnj9xRZjDxzJnQuQ'
    bot_chatID = '160968329'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    try:
        response = requests.get(send_text)
        response.json()
        return True
    except Exception:
        return False


def signal_handler(signal, frame):
    print("\nYou pressed Ctrl+C!\n")
    sys.exit(0)


def check_result(site_uri: str, status: bool):
    key = hashlib.md5(site_uri.encode('utf-8')).hexdigest()
    cache = caches[key] if key in caches else {'status': None, 'time': 0, 'error_count': 0}
    if not status:
        cache['error_count'] += 1
    else:
        cache['error_count'] = 0

    if ('status' not in cache or cache['status'] != status) or (not status and cache['time'] < time.time() - 300):
        if not status:
            message = "🚫 " + site_uri + " не доступен!" if cache['error_count'] > 0 else ""
        else:
            message = "✅ " + site_uri + " доступен!"
        if message and telegram_bot_send_text(message):
            cache['time'] = time.time()
    cache['status'] = status
    caches[key] = cache


def check_site(site_uri: str):
    # print("Check " + site_uri)
    try:
        headers = {
            'Accept-language': 'en',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15'
        }
        response = requests.get(site_uri, verify=False, headers=headers, timeout=(10, 10))
        if not response or response.status_code not in [200, 201, 301, 302]:
            print(response.status_code if response else "Not Response")
            check_result(site_uri, False)
        else:
            check_result(site_uri, True)
    except Exception as e:
        print("Exception: " + str(e))
        check_result(site_uri, False)


def read_csv_file():
    sites = []
    base_path = os.path.abspath(".")
    base_path + '/sites.csv'
    with open(base_path + '/sites.csv', newline="\n") as fp_read:
        reader = csv.reader(fp_read, delimiter=";", quotechar='"')
        for row in reader:
            if len(row) < 1:
                continue
            if len(str(row[0])) < 3:
                continue
            sites.append(row[0])


signal.signal(signal.SIGINT, signal_handler)
while True:
    read_csv_file()
    print(sites)
    for site_uri in sites:
        check_site(site_uri)
    time.sleep(10)
