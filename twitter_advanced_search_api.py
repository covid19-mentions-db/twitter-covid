import re
from twitter_utils import get_new_session, TRY_COUNTS, READ_TIMEOUT
import dateutil.parser as DP
from calculate_centroid import calculate_centroid_for_twitter_bounding_box


index_langs = ['da', 'nl', 'en', 'fi', 'fr', 'de', 'hu', 'it', 'nb', 'pt', 'ro', 'ru', 'es', 'sv', 'tr']
advanced_search_api = 'https://api.twitter.com/2/search/adaptive.json'
session = get_new_session()


def call_api(url, params):
    global session

    for _trying in range(TRY_COUNTS, -1, -1):
        try:
            resp = session.get(url, params=params, timeout=READ_TIMEOUT)
            rate_limit_remaining = resp.headers['x-rate-limit-remaining']
            print(rate_limit_remaining)

            if resp.status_code == 200:
                return resp.text, resp.json()

            if resp.status_code == 429:
                print('status_code=429, headers=', resp.headers)
                session = get_new_session()
                continue
            if rate_limit_remaining == 0:
                print('rate limit=0, headers', resp.headers)
                session = get_new_session()
                continue

            raise Exception('unexpected behavior, status_code=' + str(resp.status_code) + ', headers='
                            + str(resp.headers) + 'response=' + resp.text)

        except Exception as e:
            print(e)
            if _trying == 0:
                raise Exception('try count exceeded')


def extract_results_from_json(j, query):
    result_tweets = []

    if j:
        tweets = j['globalObjects']['tweets']
        users = j['globalObjects']['users']

        for tweet in dict(tweets).values():
            images = []
            try:
                for item in tweet['entities']['media']:
                    if item['type'] == 'photo':
                        images.append(item['media_url_https'])
            except:
                pass

            # locations from tweet
            location = None
            try:
                location = {'name': tweet['place']['full_name']}
                _location = calculate_centroid_for_twitter_bounding_box(
                    tweet['place']['bounding_box']['coordinates'][0]
                )
                location['coordinates'] = [_location[1], _location[0]]
                location['country'] = tweet['place']['country']
            except:
                pass

            # location from user
            if location is None:
                try:
                    _location = users[tweet['user_id_str']]['location']
                    if _location:
                        location = {'name': _location}
                except:
                    pass

            curr = {
                'source': 'twitter',
                'author_id': tweet['user_id_str'],
                'author_name': users[tweet['user_id_str']]['name'],
                'object_type': 'tweet',
                'object_id': tweet['id_str'],
                'object_text': tweet['text'],
                'keyword': query,
                'lang': tweet['lang'],
                'location': location,
                'time': int(DP.parse(tweet['created_at']).timestamp()),
                'likes_count': tweet['favorite_count'],
                'reposts_count': tweet['retweet_count'],
                'comments_count': tweet['reply_count'],
                'images': images,
                'new': True,
            }

            if tweet['lang'] in index_langs:
                curr['index_lang'] = tweet['lang']

            result_tweets.append(curr)

    return result_tweets


def search_tweets(query, from_date, to_date, lang=None, write_result_callback=None, limit=None):
    # query
    query_parts = [query, 'since:' + from_date, 'until:' + to_date]
    if lang:
        query_parts.append('lang:' + lang)
    q = ' '.join(query_parts)
    print('new task: "%s"' % q)

    params = {
        'q': q,
        'count': 120,
        'include_reply_count': 1,
        'cursor': '',
    }

    total = 0
    while True:
        text, j = call_api(advanced_search_api, params)
        tweets = extract_results_from_json(j, query)

        if write_result_callback and tweets:
            write_result_callback(tweets)

        total += len(tweets)

        if limit and total >= limit:
            break

        m = re.search('"(scroll:[^"]+)', text)
        if m:
            if params['cursor'] == m.group(1):
                print('there is no new cursor, end', text)
                break

            params['cursor'] = m.group(1)
            print(total, m.group(1))
            if len(tweets) == 0:
                print('tweets count=0, end', text)
                break
            continue

        print('there is no cursor, end', text)

        break

    print('parsing for', q, 'is finished')


if __name__ == '__main__':
    search_tweets('love', '2020-04-01', '2020-04-03', 'en')
