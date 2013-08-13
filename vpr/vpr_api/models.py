from django.db import models, connection, transaction
from datetime import datetime
import hashlib
import random


class Meta:
    app_label = 'VPR API'
    verbose_name = 'VPR API'


def generateClientKey(email):
    """Generate secret key for API client based on email"""
    now = str(datetime.now())
    sha = hashlib.sha224(email + now)
    sha = sha.hexdigest()[:24]
    return sha
    

def generateClientID(ip=''):
    """Generate a random, unique client ID, and ensure that it's not existing 
       in the system
    """
    new_id = ''
    while not new_id or APIClient.objects.filter(client_id=new_id):
        new_id = str(random.randint(10000000, 99999999))
    return new_id


# Create your models here.
class APIClient(models.Model):
    """ """
    client_id = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    organization = models.BooleanField()
    secret_key = models.CharField(max_length=256)
    email = models.CharField(max_length=128)
    join_date = models.DateTimeField(default=datetime.now())

    class Meta:
        verbose_name = 'API Client'

    def __unicode__(self):
        return "Client: %s (%s)" % (self.client_id, self.name)      


class APIToken(models.Model):
    """ """
    client = models.ForeignKey(APIClient)
    token = models.CharField(max_length=256)
    client_ip = models.CharField(max_length=48)
    expire = models.DateTimeField()
    since = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = 'API Token'

    def __unicode__(self):
        return "Token (%s): %s" % (self.client.client_id, self.token)


class APIRecord(models.Model):
    """ """
    client_id = models.CharField(max_length=128)
    result = models.IntegerField()
    time = models.DateTimeField()
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=256) 
    ip = models.CharField(max_length=40, blank=True, null=True) 
    query = models.CharField(max_length=256, blank=True, null=True)
    extra = models.CharField(max_length=256, blank=True, null=True)


    class Meta:
        verbose_name = 'API Record'

    def __unicode__(self):
        return "API Record: %s" % (self.request)


# MIGRATIONS

def removeVersionInPath():
    cur = connection.cursor()
    cur.execute('select id, path from vpr_api_apirecord;')
    select_records = []
    record = cur.fetchone()
    while record:
        record = list(record)
        if record[1][0] == '/':
            rf_path = '/'.join(record[1].split('/')[2:])
            select_records.append((record[0], rf_path))
        record = cur.fetchone()

    # update inside db
    for item in select_records:
        cmd = "update vpr_api_apirecord set path='%s' where id=%d;" % (item[1], item[0])
        cur.execute(cmd)
    transaction.commit_unless_managed()
