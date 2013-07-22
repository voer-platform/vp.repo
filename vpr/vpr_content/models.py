from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from django.db.models import DateTimeField, ImageField 
from hashlib import md5
from datetime import datetime

from vpr_api.models import APIClient
from repository import MaterialBase

MATERIAL_ID_SIZE = 8

# Create your models here.
class Category(models.Model):
    name = CharField(max_length=255)
    parent = IntegerField(default=0)
    description = TextField(blank=True)


class Person(models.Model):
    user_id = CharField(max_length=64)
    fullname = CharField(max_length=256, blank=True, null=True)
    email = CharField(max_length=64, blank=True, null=True)
    client_id = IntegerField(default=0)


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
        temp_id = temp_id[:MATERIAL_ID_SIZE]
        if len(Material.objects.filter(material_id=temp_id)) > 0:
            sugar += '1'
        else:
            break
    return temp_id


def assignSingleCat(material_rid, cat_id):
    mcat = MaterialCategory()
    mcat.material_rid = material_rid 
    mcat.category_id = cat_id
    mcat.save()
    return mcat


class Material(models.Model, MaterialBase):
    material_id = CharField(max_length=64, default=generateMaterialId)
    material_type = IntegerField(default=1)
    text = TextField()
    version = IntegerField(default=1)
    title = CharField(max_length=255)
    description = TextField(blank=True, null=True)
    categories = CommaSeparatedIntegerField(max_length=8, blank=True, null=True)
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


class OriginalID(models.Model):
    material_id = CharField(max_length=64, primary_key=True)
    original_id = CharField(max_length=32)


class MaterialFile(models.Model):
    material_id = CharField(max_length=64)
    version = IntegerField(default=1)
    name = CharField(max_length=255, blank=True, null=True)
    description = TextField(blank=True, null=True)
    mfile = FileField(upload_to="./mfiles")
    mime_type = CharField(max_length=100)


class MaterialExport(models.Model):
    """ Model for storing export product of the Material
    """
    material_id = CharField(max_length=64)
    version = IntegerField(default=1)
    name = CharField(max_length=255, blank=True, null=True)
    path = CharField(max_length=255)
    file_type = CharField(max_length=32, blank=True, null=True)


def getLatestMaterial(material_id):
    """ Returns the latest version of the material with given ID """
    material = Material.objects.filter(material_id=material_id)\
                                      .order_by('version') \
                                      .reverse()[0]
    return material 


def getMaterialLatestVersion(material_id):
    """ Returns the value of newest material version
    """
    material = getLatestMaterial(material_id)
    return material.version


def listMaterialFiles(material_id, version):
    """Returns all IDs of files attached to specific material, except the material image
    """
    file_ids = []
    if material_id and version:
        mfiles = MaterialFile.objects.filter(material_id=material_id, 
                                             version=version)
        file_ids = [mf.id for mf in mfiles]

    return file_ids   



# MIGRATION

