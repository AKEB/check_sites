import requests
import time
import signal
import sys
import hashlib
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


sites = [
    'https://akeb.ru/',
    'https://ats.my.games/',
]

caches = {}


def telegram_bot_sendtext(bot_message):
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
    cache = caches[key] if key in caches else {'status': None, 'time': 0}
    if ('status' not in cache or cache['status'] != status) or (not status and cache['time'] < time.time() - 300):
        if not status:
            message = "🚫 " + site_uri + " не доступен!"
        else:
            message = "✅ " + site_uri + " доступен!"
        if telegram_bot_sendtext(message):
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


signal.signal(signal.SIGINT, signal_handler)
while True:
    for site_uri in sites:
        check_site(site_uri)
    time.sleep(5)
