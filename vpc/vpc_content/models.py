from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from hashlib import md5
from datetime import datetime

from vpc_api.models import APIClient


# Create your models here.
class Category(models.Model):
    name = CharField(max_length=255)
    parent = IntegerField(default=0)
    description = TextField(blank=True)


class Author(models.Model):
    fullname = CharField(max_length=255)
    bio = TextField(blank=True)


class Editor(models.Model):
    fullname = CharField(max_length=255, blank=True)
    user_id = CharField(max_length=64, blank=True)
    client_id = IntegerField(default=0)


def generateModuleId():
    """ Ensure generating of unique module ID
    """
    sugar = ''
    while True:
        temp_id = md5(str(datetime.now) + sugar).hexdigest()
        if len(Module.objects.filter(module_id=temp_id)) > 0:
            sugar += '1'
        else:
            break
    return temp_id


class Module(models.Model):
    module_id = CharField(max_length=32, default=generateModuleId)
    text = TextField()
    version = CharField(max_length=32, default='1')
    title = CharField(max_length=255)
    description = TextField()
    categories = CommaSeparatedIntegerField(max_length=8)
    authors = CommaSeparatedIntegerField(max_length=8)
    editor_id = IntegerField()
    keywords = TextField()
    file = FileField(upload_to=".", null=True)
    file_type = CharField(max_length=64, blank=True)
