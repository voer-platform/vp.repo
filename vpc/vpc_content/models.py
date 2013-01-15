from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from django.db.models import DateTimeField
from hashlib import md5
from datetime import datetime

from vpc_api.models import APIClient
from repository import MaterialBase


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

# (HP) I don't think we will use this anymore.
# Using normal pk field would be good enough.
def generateMaterialId():
    """ Ensure generating of unique material ID
    """
    sugar = ''
    while True:
        temp_id = md5(str(datetime.now) + sugar).hexdigest()
        if len(Material.objects.filter(material_id=temp_id)) > 0:
            sugar += '1'
        else:
            break
    return temp_id


class Material(models.Model, MaterialBase):
    material_id = CharField(max_length=64, default=generateMaterialId)
    text = TextField()
    version = IntegerField()
    title = CharField(max_length=255)
    description = TextField()
    categories = CommaSeparatedIntegerField(max_length=8)
    authors = CommaSeparatedIntegerField(max_length=8)
    editor_id = IntegerField()
    keywords = TextField()
    file = FileField(upload_to=".", null=True)
    file_type = CharField(max_length=64, blank=True)
    language = CharField(max_length=2, blank=True)
    license_id = IntegerField(null=True)
    modified = DateTimeField(default=datetime.now)


