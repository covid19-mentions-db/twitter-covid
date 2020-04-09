import requests
import re
import random


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


# load proxies from proxies.txt file
# you have to place it on root folder of this project
with open('proxies.txt', 'r') as f:
    content = f.readlines()
PROXIES = [x.strip() for x in content]
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

            # set proxy
            _proxy = random.choice(PROXIES)
            _proxy = {'https': 'http://%s' % _proxy}
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
