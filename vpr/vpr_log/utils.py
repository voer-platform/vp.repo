from pymongo import MongoClient
from django.conf import settings


def getLogDatabase():
    config = settings.LOG_DATABASE
    client = MongoClient(config['host'], config['port'])
    return client[config['name']]


log_db = getLogDatabase()


# Do we really need this one?
def initLogDatabase():
    """Create new log database and api collection in MongoDB if missing"""
    config = settings.LOG_DATABASE
    client = MongoClient(config['host'], config['port'])
    db_name = config['name']
    col_name = settings.LOG_COLLECTION['api']
    if db_name not in client.database_names():
        client[db_name].create_collection(col_name)
    elif col_name not in client[db_name].collection_names():
        client[db_name].create_collection(col_name)
    # that's it!


def saveLog(collection, record):
    global log_db
    try:
        collection = log_db[collection]
        collection.insert(record)
    except:
        # reconnect to the database and missing current log
        log_db = getLogDatabase()

