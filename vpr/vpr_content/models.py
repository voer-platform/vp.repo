from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from django.db.models import DateTimeField, ImageField
from hashlib import md5
from datetime import datetime

from vpr_api.models import APIClient
from repository import MaterialBase


# Create your models here.
class Category(models.Model):
    name = CharField(max_length=255)
    parent = IntegerField(default=0)
    description = TextField(blank=True)


class Author(models.Model):
    fullname = CharField(max_length=255)
    text = TextField(blank=True)


class Editor(models.Model):
    fullname = CharField(max_length=255, blank=True)
    user_id = CharField(max_length=64, blank=True)
    client_id = IntegerField(default=0)

# (z) I don't think we will use this anymore.
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
    material_type = IntegerField(default=1)
    text = TextField()
    version = IntegerField(default=1)
    title = CharField(max_length=255)
    description = TextField()
    categories = CommaSeparatedIntegerField(max_length=8)
    authors = CommaSeparatedIntegerField(max_length=8)
    editor_id = IntegerField()
    keywords = TextField(blank=True, null=True)
    #file = FileField(upload_to=".", null=True)
    #file_type = CharField(max_length=64, blank=True)
    language = CharField(max_length=2, blank=True)
    license_id = IntegerField(null=True)
    modified = DateTimeField(default=datetime.now)
    derived_from = CharField(max_length=64, blank=True, null=True)
    image = ImageField(upload_to="./mimgs", blank=True, null=True) 


class MaterialFile(models.Model):
    material_id = CharField(max_length=64)
    version = IntegerField(default=1)
    name = CharField(max_length=255, blank=True, null=True)
    description = TextField(blank=True, null=True)
    mfile = FileField(upload_to="./mfiles")
    mime_type = CharField(max_length=100)


def listMaterialFiles(material_id, version):
    """Returns all IDs of files attached to specific material, except the material image
    """
    file_ids = []
    if material_id and version:
        mfiles = MaterialFile.objects.filter(material_id=material_id, 
                                             version=version)
        file_ids = [mf.id for mf in mfiles]

    return file_ids   

class MaterialExport(models.Model):
    """ Model for storing export product of the Material
    """
    material_id = CharField(max_length=64)
    version = IntegerField(default=1)
    name = CharField(max_length=255, blank=True, null=True)
    path = CharField(max_length=255)
    file_type = CharField(max_length=32, blank=True, null=True)

