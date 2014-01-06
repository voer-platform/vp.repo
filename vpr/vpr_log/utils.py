from pymongo import MongoClient, DESCENDING 
from django.conf import settings




def cleanLog(collection, day_limit=30):
    """ Clean all the log records inside collection older than day_limit
    """
    pass  

