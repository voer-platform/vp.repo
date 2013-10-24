from rest_framework import serializers
from vpr_content import models


class MaterialSerializer(serializers.ModelSerializer):

    modified = serializers.DateTimeField(read_only=True)
    material_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Material
        fields = ('material_id', 'material_type', 'title', 'text', 
                  'version', 'description', 'categories', 'keywords', 
                  'image', 'language', 'license_id', 'modified', 
                  'derived_from',)

    def convert_object(self, obj):
        """
        Core of serialization.
        Convert an object into a dictionary of serialized field values.
        """
        ret = self._dict_class()
        ret.fields = {}

        fields = self.get_fields(nested=bool(self.opts.depth))
        for field_name, field in fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field

        # vpr: custom settings for categories field
        cids = models.restoreAssignedCategory(ret.get('categories', ''))
        cids = [str(cid) for cid in cids]
        ret['categories'] = ','.join(cids)

        # vpr: custom process for material author, editor
        material_roles = models.getMaterialPersons(obj.id)
        for person_role in material_roles:
            ret[person_role] = material_roles[person_role] 

        return ret


    def restore_object(self, attrs, instance=None):
        """
        Restore the model instance.
        """
        self.m2m_data = {}

        # vpr: standardize the entered category
        attrs['categories'] = models.refineAssignedCategory(
            attrs.get('categories', ''))

        if instance:
            for key, val in attrs.items():
                setattr(instance, key, val)
            return instance

        # Reverse relations
        for (obj, model) in self.opts.model._meta.get_all_related_m2m_objects_with_model():
            field_name = obj.field.related_query_name()
            if field_name in attrs:
                self.m2m_data[field_name] = attrs.pop(field_name)

        # Forward relations
        for field in self.opts.model._meta.many_to_many:
            if field.name in attrs:
                self.m2m_data[field.name] = attrs.pop(field.name)

        return self.opts.model(**attrs)


class CategorySerializer(serializers.ModelSerializer):
    """docstring for CategorySerializer"""
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent', 'description')


class PersonSerializer(serializers.ModelSerializer):
    """docstring for PersonSerializer"""
    class Meta:
        model = models.Person
        fields = ('id', 'fullname', 'first_name', 'last_name', 'title',
                  'user_id', 'email', 'client_id', 'homepage', 'affiliation',
                  'affiliation_url', 'national', 'biography', 'avatar')


class MiniPersonSerializer(serializers.ModelSerializer):
    """docstring for PersonSerializer"""
    class Meta:
        model = models.Person
        fields = ('id', 'fullname', 'first_name', 'last_name', 'title',
                  'user_id', 'email', 'client_id')


class IndexPersonSerializer(serializers.ModelSerializer):
    """docstring for PersonSerializer"""
    class Meta:
        model = models.Person
        fields = ('id', 'fullname', 'first_name', 'last_name', 'title',
                  'user_id', 'email')

    def convert_object(self, obj):
        ret = self._dict_class()
        ret.fields = {}

        fields = self.get_fields(nested=bool(self.opts.depth))
        for field_name, field in fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field

        # vpr: custom settings for categories field
        ret['id'] = obj.pk 

        return ret


class MaterialFileSerializer(serializers.ModelSerializer):
    """ File attached to material """
    class Meta:
        model = models.MaterialFile
        fields = ('id', 'material_id', 'version', 
                  'name', 'description', 
                  'mfile', 'mime_type')

# SERIALIZERS FOR SEARCHING

class IndexMaterialSerializer(serializers.Serializer):
    
    material_id = serializers.Field()
    title = serializers.Field()
    material_type = serializers.Field()
    version = serializers.Field()
    modified = serializers.Field()
    categories = serializers.Field()

    def convert_object(self, obj):
        """
        Core of serialization.
        Convert an object into a dictionary of serialized field values.
        """
        ret = self._dict_class()
        ret.fields = {}

        fields = self.get_fields(nested=bool(self.opts.depth))
        for field_name, field in fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field

        # vpr: custom settings for categories field
        cids = models.restoreAssignedCategory(ret.get('categories', ''))
        cids = [str(cid) for cid in cids]
        ret['categories'] = ','.join(cids)

        # vpr: custom process for material author, editor
        material_roles = models.getMaterialPersons(obj.pk)
        for person_role in material_roles:
            ret[person_role] = material_roles[person_role] 

        return ret
