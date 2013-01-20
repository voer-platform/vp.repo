import datetime
from haystack import indexes, site
from models import Author


class AuthorIndex(indexes.SearchIndex):
    fullname = indexes.CharField(use_template=True)
    bio = indexes.CharField(document=True, use_template=True)

    def index_queryset(self):
        """Used when entire index for model is updated"""
        #return Author.objects.filter(pub_date__lte=datetime.datetime.now())
        return Author.objects.all()

site.register(Author, AuthorIndex)
