from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import OneToOneField, ManyToManyField, ForeignKey
from hashlib import md5
from datetime import datetime

from vpc_api.models import APIClient


# Create your models here.
class Category(models.Model):
    name = CharField(max_length=255)
    description = TextField()


class Author(models.Model):
    fullname = CharField(max_length=255)
    author_id = CharField(max_length=255)
    bio = TextField()


class Editor(models.Model):
    editor_id = CharField(max_length=255)
    client = OneToOneField(APIClient)
    

class Metadata(models.Model):
    title = CharField(max_length=255)
    description = TextField()
    categories = ManyToManyField(Category)
    authors = ManyToManyField(Author)
    keywords = TextField()
    editor = OneToOneField(Editor)


class Attachment(models.Model):
    """Class for module attachment"""
    data_type = CharField(max_length=255)
    raw = FileField(upload_to=".")
    

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
    metadata = OneToOneField(Metadata)
    attachment = ForeignKey(Attachment, null=True, blank=True, unique=True)
    version = CharField(max_length=32, default='1')
    client_id = CharField(max_length=255)


