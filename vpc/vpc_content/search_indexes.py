import datetime
from haystack import indexes, site
from models import Author


class AuthorIndex(indexes.SearchIndex):
    fullname = indexes.CharField(document=True, use_template=True)
    bio = indexes.CharField(document=True, use_template=True)
    
