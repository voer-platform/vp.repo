from django.db import models

from django.db.models import CharField, TextField, FileField
from django.db.models import OneToOneField, ManyToManyField
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
    

class Module(models.Model):
    text = TextField()
    metadata = OneToOneField(Metadata)
    attachment = OneToOneField(Attachment)
    version = CharField(max_length=32)
    client_id = CharField(max_length=255)