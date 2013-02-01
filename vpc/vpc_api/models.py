from django.db import models
from datetime import datetime


class Meta:
    app_label = 'VPC API'
    verbose_name = 'VPC API'


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


# 
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
    client_id = models.ForeignKey(APIClient)
    result = models.IntegerField()
    time = models.DateTimeField()
    type = models.IntegerField()
    request = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'API Record'

    def __unicode__(self):
        return "API Record: %s" % (self.request)
