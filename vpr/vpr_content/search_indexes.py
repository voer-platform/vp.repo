import datetime
from haystack.indexes import SearchIndex, RealTimeSearchIndex
from haystack.indexes import CharField, DateTimeField
from haystack import site
from models import Material, Person 


class MaterialIndex(RealTimeSearchIndex):
    # "text" combines normal body, title, description and keywords
    text = CharField(document=True, use_template=True)
    material_id = CharField(model_attr='material_id')
    title = CharField(model_attr='title')
    description = CharField(model_attr='description')
    modified = DateTimeField(model_attr='modified')
    material_type = DateTimeField(model_attr='material_type')

    def index_queryset(self):
        """When entired index for model is updated"""
        return Material.objects.all()


class PersonIndex(RealTimeSearchIndex):
    # "text" combines normal body, title, description and keywords
    text = CharField(document=True, use_template=True)
    user_id = CharField(model_attr='user_id')
    email = CharField(model_attr='email')

    def index_queryset(self):
        """When entired index for model is updated"""
        return Person.objects.all()


site.register(Material, MaterialIndex)
site.register(Person, PersonIndex)
