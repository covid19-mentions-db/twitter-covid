import os
import pika
import datetime
import json
import hashlib
import pymongo
import twitter_advanced_search_api


# get params from virtual environment
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT'))
rabbitmq_queue = os.getenv('RABBITMQ_QUEUE')
rabbitmq_user = os.getenv('RABBITMQ_USER')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
#
mongodb_host = os.getenv('MONGODB_HOST')
mongodb_port = int(os.getenv('MONGODB_PORT'))
mongodb_db = os.getenv('MONGODB_DB')
mongodb_task_collection = os.getenv('MONGODB_TASK_COLLECTION')
mongodb_result_collection = os.getenv('MONGODB_RESULT_COLLECTION')
mongodb_user = os.getenv('MONGODB_USER')
mongodb_password = os.getenv('MONGODB_PASSWORD')
mongodb_auth_db = os.getenv('MONGODB_AUTH_DB')


print('connect rabbirmq')
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

#
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
task_collection = db[mongodb_task_collection]
# create index, if exists - it won't create an error, just ignores
result_collection.create_index([("source", pymongo.ASCENDING),
                                ("object_type", pymongo.ASCENDING),
                                ("object_id", pymongo.ASCENDING)],
                               unique=True)


task = {}


def result_write_callback(posts):
    # insert result
    try:
        result_collection.insert_many(posts, ordered=False)
    except pymongo.errors.BulkWriteError as e:
        print(len(e.details['writeErrors']), '-')
        if not e.details['writeErrors'][0]['errmsg'].startswith('E11000 duplicate key error collection'):
            raise e


def callback(ch, method, properties, body):
    print(1)
    global task
    # task ans hash
    task = json.loads(body)
    task_keys = dict(task).keys()
    list(task_keys).sort()
    task_values = [str(task[key]) for key in task_keys]
    str_to_get_hash = 'twitter-advanced-search-api' + ''.join(task_values)
    result = hashlib.md5(str_to_get_hash.encode())
    task_hash = result.hexdigest()

    # parse if the same task had not been done already
    task_in_db = task_collection.find({'_id': task_hash})
    if not task_in_db.count():
        # parse
        twitter_advanced_search_api.search_tweets(
            query=task['query'],
            limit=task['limit'],
            from_date=task['from_date'],
            to_date=task['to_date'],
            lang=task['lang'],
            write_result_callback=result_write_callback,
        )

        # task log 1
        try:
            created_at = int(datetime.datetime.now().timestamp())
            task_collection.insert_one({'_id': task_hash, 'created_at': created_at, 'task': task})
        except pymongo.errors.DuplicateKeyError as e:
            print('pymongo.errors.DuplicateKeyError', task_hash, e)
    else:
        print('task', task_hash, 'is already exists', json.dumps(task))
    print(2)

    # task is done
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(3)


# start RABBITMQ consumer
print('start consumer')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=callback, queue=rabbitmq_queue)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
