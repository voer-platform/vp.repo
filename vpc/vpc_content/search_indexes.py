import datetime
from haystack.indexes import SearchIndex, CharField
from haystack import site
from models import Author, Material


class AuthorIndex(SearchIndex):
    fullname = CharField()
    text = CharField(document=True)

    def index_queryset(self):
        """Used when entire index for model is updated"""
        #return Author.objects.filter(pub_date__lte=datetime.datetime.now())
        return Author.objects.all()


class MaterialIndex(SearchIndex):
    text = CharField(document=True)
    title = CharField()
    description = CharField()
    keywords = CharField()

    def index_queryset(self):
        """When entired index for model is updated"""
        return Material.objects.all()


site.register(Author, AuthorIndex)
site.register(Material, MaterialIndex)
