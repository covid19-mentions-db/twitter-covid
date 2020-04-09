import os
import pika
import datetime
import json


# get params from virtual environment
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT'))
rabbitmq_queue = os.getenv('RABBITMQ_QUEUE')
rabbitmq_user = os.getenv('RABBITMQ_USER')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')

# RABBITMQ config
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection_parameters = pika.ConnectionParameters(
    host=rabbitmq_host,
    port=rabbitmq_port,
    heartbeat=0,
    credentials=credentials
)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue, durable=True)


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
# date range
start_time = datetime.datetime.strptime('Dec 1 2019', '%b %d %Y')
_delta = datetime.datetime.now() - start_time
numdays = _delta.days
base = datetime.datetime.today()
dates = [base - datetime.timedelta(days=x) for x in range(1, numdays + 1)]  # from start time to yesterday


i = 0
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

            channel.basic_publish(exchange='',
                                  routing_key=rabbitmq_queue,
                                  body=json.dumps(task),
                                  properties=pika.BasicProperties(
                                      delivery_mode=2,  # make message persistent
                                  ))
            i += 1
            print(i, json.dumps(task))

print('finish publishing')
# finish work
connection.close()
