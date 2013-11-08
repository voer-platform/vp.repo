from pymongo import MongoClient, DESCENDING 
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


def filterLog(collection, limitation=100, **kwargs):
    """ Extract and returns logs following given conditions
    """
    global log_db
    col = log_db[collection]
    query = {}

    if 'start' in kwargs or 'end' in kwargs:
        query['time'] = {}
    if kwargs.get('start', None):
        query['time']['$gte'] = kwargs['start']
    if kwargs.get('end', None):
        query['time']['$lt'] = kwargs['end']
    
    print query

    res = col.find(query).sort('time', DESCENDING).limit(limitation)
    logs = [item for item in res]

    return logs


def cleanLog(collection, day_limit=30):
    """ Clean all the log records inside collection older than day_limit
    """
    pass  
