import datetime
from haystack.indexes import SearchIndex, Indexable
from haystack.indexes import CharField, DateTimeField, IntegerField
from models import Material, Person 


class MaterialIndex(SearchIndex, Indexable):
    # "text" combines normal body, title, description and keywords
    text = CharField(document=True, use_template=True)
    material_id = CharField(model_attr='material_id')
    title = CharField(model_attr='title')
    description = CharField(model_attr='description')
    modified = DateTimeField(model_attr='modified')
    material_type = IntegerField(model_attr='material_type')

    def get_model(self):
        return Material

    def index_queryset(self, using=None):
        """When entired index for model is updated"""
        return self.get_model().objects.all()


class PersonIndex(SearchIndex, Indexable):
    # "text" combines normal body, title, description and keywords
    text = CharField(document=True, use_template=True)
    user_id = CharField(model_attr='user_id')
    email = CharField(model_attr='email')

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        """When entired index for model is updated"""
        return self.get_model().objects.all()


