from pymongo import MongoClient, DESCENDING 
from django.conf import settings

from base import BaseLogHandler


class MongoDBHandler(BaseLogHandler):
    """ Provide basic functions for saving/storing logs into MongoDB
    """
    log_db = None

    def __init__(self):
        self.log_db = getMongoDB()

    def store(self, record):
        try:
            collection = self.log_db[record.logset]
            log_dict = record.__dict__
            del log_dict['logset']
            collection.insert(log_dict)
        except:
            # reconnect to the database and drop current log
            self.log_db = getMongoDB()

    def clean(self, collection, day_limit=30):
        """ Clean all the log records inside collection older than day_limit
        """
        pass  

    def filter(self, collection, limitation=100, **kwargs):
        """ Extract and returns logs following given conditions
        """
        col = self.log_db[collection]
        query = {}

        if 'start' in kwargs or 'end' in kwargs:
            query['time'] = {}
        if kwargs.get('start', None):
            query['time']['$gte'] = kwargs['start']
        if kwargs.get('end', None):
            query['time']['$lt'] = kwargs['end']
        
        res = col.find(query).sort('time', DESCENDING).limit(limitation)
        logs = [item for item in res]

        return logs


def getMongoDB():
    """ Connect and return connection to MongoDB
    """
    config = settings.VPR_LOG_DATABASES['mongodb']
    client = MongoClient(config['host'], config['port'])
    return client[config['name']]


