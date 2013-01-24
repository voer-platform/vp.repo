# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from django.http import Http404
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from hashlib import md5
from datetime import datetime
from rest_framework import mixins
from haystack.query import SearchQuerySet 

import models
import serializers

def dispatchModuleCalls(request):
    """ Analyze the requests and call the appropriate function
    """
    # analyze the URL
    path = splitPath(path)
    if request.method == 'POST':
        params = request.POST
        params['path'] = path
        if len(path) > 1:
            checkInModule(params)
        else:
            createModule(params)
    elif request.method == 'GET':
        # check if getting metadata or download
        if 'content' in request.GET:
            download = request.GET['content']
        if download:
            downloadModule(request)
        else:    
            getModuleMetadata(request)
    elif request.method == 'DELETE':
        # check for permission
        user = request.user
        if user.is_superuser:
            deleteModule(request)
        else:
            pass


def splitPath(path):
    """ Return necessary elements in path
        
        >>> path = '/hello/from/paris/'
        >>> splitPath(path)
        ['hello', 'from', 'paris']

    """
    path = path.split('/')
    path = [item for item in path if len(item)>0]
    return path


# CATEGORY CALLS

class CategoryList(generics.ListCreateAPIView):
    """docstring for AuthorList"""
    model = models.Category
    serializer_class = serializers.CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for CategoryDetail"""
    model = models.Category
    serializer_class = serializers.CategorySerializer


# EDITOR CALLS

class EditorList(generics.ListCreateAPIView):
    """docstring for EditorList"""
    model = models.Editor
    serializer_class = serializers.EditorSerializer


class EditorDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for EditorDetail"""
    model = models.Editor
    serializer_class = serializers.EditorSerializer


# AUTHOR CALLS

class AuthorList(generics.ListCreateAPIView):
    """docstring for AuthorList"""
    model = models.Author
    serializer_class = serializers.AuthorSerializer


class AuthorDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for AuthorDetail"""
    model = models.Author
    serializer_class = serializers.AuthorSerializer

# MODULE

class MaterialList(generics.ListCreateAPIView):
    """ Return list of material or create a new one
    """
    model = models.Material
    serializer_class = serializers.MaterialSerializer
    br_fields = ('categories', 'authors', 'editor_id', 
                 'language', 'material_type')

    def list(self, request, *args, **kwargs):
        """ Customized function for listing materials with same ID
        """
        try: 
            m_objects = self.model.objects
            if kwargs.get('mid', None):
                self.object_list = m_objects.filter(material_id=kwargs['mid'])
            else:
                self.object_list = m_objects.all()
            # do the filtering
            browse_on = {}
            fields = [item for item in request.GET if item in self.br_fields]
            [browse_on.update({item:request.GET[item]}) for item in fields]
            self.object_list = self.object_list.filter(**browse_on)
            # continue with sorting
            sort_fields = request.GET.get('sort_on', '')
            if sort_fields:
                self.object_list = self.object_list.order_by(sort_fields)
        except:
            raise Http404()

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            error_args = {'class_name': self.__class__.__name__}
            raise Http404(self.empty_error % error_args)

        # Pagination size is set by the `.paginate_by` attribute,
        # which may be `None` to disable pagination.
        page_size = self.get_paginate_by(self.object_list)
        if page_size:
            packed = self.paginate_queryset(self.object_list, page_size)
            paginator, page, queryset, is_paginated = packed
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list)

        return Response(serializer.data)

    #def get(self, request, *args, **kwargs):
    #    """docstring for get"""
    #    return Response({'a':'b'})

class MaterialDetail(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    """
    Return material data, update/check-in it or delete it
    """
    model = models.Material
    serializer_class = serializers.MaterialSerializer

    def get_object(self, material_id, version=''):
        """ Customized get_object() function, used for Material objects
            which will be get by ID and version.
        """
        try:
            args = {'material_id':material_id}
            # get latest or specific version
            object = self.model.objects
            if version:
                args['version'] = version
                object = object.get(**args)
            else:
                object = getLatestMaterial(material_id)
            return object 
        except:
            raise Http404()

    def retrieve(self, request, *args, **kwargs):
        """ Customized to the Material objects """
        self.object = self.get_object(material_id=kwargs.get('mid', ''),
                                      version=kwargs.get('version', ''))
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        """docstring for get"""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """ Check in a material  """
        try: 
            serializer = self.get_serializer(data=request.DATA)
            if serializer.is_valid():
                # check if valid editor or new material will be created
                sobj = serializer.object
                last_material = getLatestMaterial(sobj.material_id)
                last_editor = ""
                try:    
                    last_editor = last_material.editor_id
                except AttributeError:
                    pass 
                # new material will have new ID
                if sobj.editor_id != last_editor:
                    sobj.material_id = models.generateMaterialId()
                    sobj.version = 1
                else:
                    try:
                        sobj.version = last_material.version + 1
                    except AttributeError:
                        sobj.version = 1
                self.pre_save(sobj)
                self.object = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        except: 
            return Http404

    def destroy(self, request, *args, **kwargs):
        """ Delete the material """
        try:
            self.object = self.get_object(material_id=kwargs.get('mid', ''),
                                          version=kwargs.get('version', ''))
            self.object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Http404

class SearchMaterial(generics.ListAPIView):
    """docstring for Search"""
    model = models.Material
    serializer_class= serializers.MiniMaterialSerializer

    def list(self, request, *args, **kwargs):
        """docstring for list"""
        try:
            self.object_list = SearchQuerySet().filter(content=kwargs['keyword'])
        except:
            return Http404

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            error_args = {'class_name': self.__class__.__name__}
            raise Http404(self.empty_error % error_args)

        # Pagination size is set by the `.paginate_by` attribute,
        # which may be `None` to disable pagination.
        page_size = self.get_paginate_by(self.object_list)
        if page_size:
            packed = self.paginate_queryset(self.object_list, page_size)
            paginator, page, queryset, is_paginated = packed
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list)

        return Response(serializer.data) 

def getLatestMaterial(mid):
    """ Returns the latest version of the material with given ID """
    material = None
    try:
        material = models.Material.objects.filter(material_id=mid)\
                                          .order_by('version') \
                                          .reverse()[0]
    except:
        pass
    return material 
