import os
import datetime
import twitter_advanced_search_api
import pymongo


mongodb_host = os.getenv('MONGODB_HOST')
mongodb_port = int(os.getenv('MONGODB_PORT'))
mongodb_db = os.getenv('MONGODB_DB')
mongodb_result_collection = os.getenv('MONGODB_RESULT_COLLECTION')
mongodb_user = os.getenv('MONGODB_USER')
mongodb_password = os.getenv('MONGODB_PASSWORD')
mongodb_auth_db = os.getenv('MONGODB_AUTH_DB')

#
days_count = int(os.getenv('DAYS_COUNT', 3))


print('connect mongodb')
# MONGODB config
client = pymongo.MongoClient(
    mongodb_host,
    mongodb_port,
    username=mongodb_user,
    password=mongodb_password,
    authSource=mongodb_auth_db
)
db = client[mongodb_db]
result_collection = db[mongodb_result_collection]
# create index, if exists - it won't create an error, just ignores
result_collection.create_index([("source", pymongo.ASCENDING),
                                ("object_type", pymongo.ASCENDING),
                                ("object_id", pymongo.ASCENDING)],
                               unique=True)


# languages
languages = [None]
# queries
queries = ['covid-19', 'covid', 'coronavirus', 'SARS-CoV-2', 'SARS-CoV2', '2019-nCoV', 'коронавирус',"covıd",
           "covid19", "covıd19", "covi̇d19", "covi̇d_19", "covid2020", "covidmemes", "coronavid19", "covod19",
           "coronavairus", "cvid19", "covidiot", "novelcorona", "covidindia", "pandemic2020", "covidkindness",
           "pandemicpreparedness", "covidnews", "2019ncov", "sarscov2", "sars_cov_2", "coronaeurope", "coronausa",
           "coronaworld", "coronachina", "coronacapital", "coronaupdate", "coronaextra", "instacorona",
           "coronawuhan", "coronaitaly", "coronavırusnews", "covid20", "cốvịdịch", "coronacases", "pandemic",
           "coronaprotection", "coronacure", "coronafight", "coronasymptoms", "sarcov2", "covidgermany",
           "ncov", "ncov2019", "ncov2020", "2019ncov"]
queries = queries + ['(#%s)' % query for query in queries]
# get date range
base = datetime.datetime.today()
dates = [base - datetime.timedelta(days=x) for x in range(0, days_count)]


def result_write_callback(posts):
    # insert result
    try:
        result_collection.insert_many(posts, ordered=False)
    except pymongo.errors.BulkWriteError as e:
        print(len(e.details['writeErrors']), '-')
        if not e.details['writeErrors'][0]['errmsg'].startswith('E11000 duplicate key error collection'):
            raise e


# publish tasks
for query in queries:
    for language in languages:
        for date in dates:
            task = {
                'query': query,
                'limit': 0,
                'from_date': date.strftime("%Y-%m-%d"),
                'to_date': (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                'lang': language,
            }

            twitter_advanced_search_api.search_tweets(
                query=task['query'],
                limit=task['limit'],
                from_date=task['from_date'],
                to_date=task['to_date'],
                lang=task['lang'],
                write_result_callback=result_write_callback,
            )

print('finish publishing')
