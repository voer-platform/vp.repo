from rest_framework import serializers

from vpc_content import models


#class MetadataSerializer(serializers.ModelSerializer):
#    title = serialize.Field()
#    description = serialize.Field()
#    keywords = serialize.Field()


class ModuleSerializer(serializers.ModelSerializer):
    #module_id = serializers.CharField()
    #version = serializers.CharField()
    #client_id = serializers.CharField()
    class Meta:
        model = models.Module
        fields = ('module_id', 'version', 'client_id')
        

class AuthorSerializer(serializers.ModelSerializer):
    """docstring for AuthorSerializer"""
    class Meta:
        model = models.Author
        fields = ('id', 'fullname', 'bio')


class CategorySerializer(serializers.ModelSerializer):
    """docstring for CategorySerializer"""
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent', 'description')


class EditorSerializer(serializers.ModelSerializer):
    """docstring for EditorSerializer"""
    client = serializers.IntegerField()
    class Meta:
        model = models.Editor
        fields = ('id', 'fullname', 'client_id')

