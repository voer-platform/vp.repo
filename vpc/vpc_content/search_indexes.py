import datetime
from haystack.indexes import SearchIndex, CharField
from haystack import site
from models import Author, Material


class AuthorIndex(SearchIndex):
    # the used template contains fullname and author bio
    # Zniper thinks this line below also is OK:
    # text = CharField(document=True, model_attr='text')
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        """Used when entire index for model is updated"""
        return Author.objects.all()


class MaterialIndex(SearchIndex):
    # "text" combines normal body, title, description and keywords
    text = CharField(document=True, use_template=True)
    material_id = CharField(model_attr='material_id')

    def index_queryset(self):
        """When entired index for model is updated"""
        return Material.objects.all()


site.register(Author, AuthorIndex)
site.register(Material, MaterialIndex)
