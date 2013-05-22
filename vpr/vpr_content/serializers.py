from rest_framework import serializers
from vpr_content import models


class MaterialSerializer(serializers.ModelSerializer):
    #material_id = serializers.Field()
    #version = serializers.Field()
    modified = serializers.Field()

    class Meta:
        model = models.Material
        fields = ('material_id', 'material_type', 'title', 'text', 
                  'version', 'description', 'categories', 'authors',
                  'editor_id', 'keywords', 'image', 'language', 
                  'license_id', 'modified', 'derived_from',)


class AuthorSerializer(serializers.ModelSerializer):
    """docstring for AuthorSerializer"""
    class Meta:
        model = models.Author
        fields = ('id', 'fullname', 'text')


class CategorySerializer(serializers.ModelSerializer):
    """docstring for CategorySerializer"""
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent', 'description')


class EditorSerializer(serializers.ModelSerializer):
    """docstring for EditorSerializer"""
    class Meta:
        model = models.Editor
        fields = ('id', 'fullname', 'user_id', 'client_id')


class MaterialFileSerializer(serializers.ModelSerializer):
    """ File attached to material """
    class Meta:
        model = models.MaterialFile
        fields = ('id', 'material_id', 'version', 'mfile', 'mime_type')

# SERIALIZERS FOR SEARCHING

class MiniMaterialSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Material
        fields = ('material_id', 'material_type', 'title',
                  'description', 'version', 'authors', 'editor_id',
                  'modified')
