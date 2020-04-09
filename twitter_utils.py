import requests
import re
import random
import os


twitter_main_url = 'https://twitter.com/'  # to get guest token
twitter_user_lookup_api = 'https://api.twitter.com/1.1/users/lookup.json'  # to get user location
initial_headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 '
                  'Safari/537.36',
}  # to work with twitter_user_lookup_api
authorization_headers = {
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cH'
                     'jhLTvJu4FA33AGWWjCpTnA',
}


USE_PROXY = False
PROXIES_FILE_PATH_OR_URL = os.getenv('PROXIES_FILE_PATH_OR_URL')
PROXIES_TYPE = os.getenv('PROXIES_TYPE')
if PROXIES_FILE_PATH_OR_URL:
    m = re.search('^http(?:s|)://', PROXIES_FILE_PATH_OR_URL)
    if m:
        resp = requests.get(PROXIES_FILE_PATH_OR_URL)
        content = resp.text
    else:
        with open(PROXIES_FILE_PATH_OR_URL, 'r') as f:
            content = f.readlines()

    PROXIES = [x.strip() for x in content]
    USE_PROXY = True


READ_TIMEOUT = 30
TRY_COUNTS = 10


# get nes session with random proxy and guest token
def get_new_session():
    print('start getting new session')
    for _trying in range(TRY_COUNTS, -1, -1):
        try:
            # init session with default headers
            session = requests.session()
            session.headers.update(initial_headers)

            if USE_PROXY:
                # set proxy
                _proxy = random.choice(PROXIES)
                _proxy = {'https': '%s://%s' % (PROXIES_TYPE, _proxy)}
                session.proxies = _proxy

            # get new guest token
            resp = session.get(twitter_main_url)
            resp_text = resp.text
            m = re.search('"gt=(\d+)', resp_text)
            x_guest_token = m.group(1)

            # set required headers
            new_authorization_headers = authorization_headers.copy()
            new_authorization_headers['x-guest-token'] = x_guest_token
            session.headers.update(new_authorization_headers)

            print('getting new session successful')
            return session

        except Exception as e:
            print(e)
            if _trying == 0:
                raise Exception('try count exceeded')
