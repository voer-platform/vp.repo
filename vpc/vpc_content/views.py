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


def createAuthor(fullname, author_id, bio):
    """ Creates new author inside database, or
        just returns object if existing
    """
    author = None 
    try:
        author = models.Author.objects.filter(author_id=author_id)
        if len(author) > 0:
            author = author[0]
        else:
            new_author = models.Author()
            new_author.fullname = fullname
            new_author.author_id = author_id 
            new_author.bio = bio
            new_author.save()
            author = new_author
    except:
        raise
    return author


def createEditor(editor_id, client):
    """ Create new editor inside repository
        Parameters:
            e_id   ID of the editor in the client system
            client      APIClient object which makes request
    """
    editor = None
    try:
        editor = models.Editor.objects.filter(editor_id=editor_id)
        if len(editor) > 0:
            editor = editor[0]
        else:
            editor = models.Editor()
            editor.editor_id = editor_id
            editor.client = client
            editor.save()
    except:
        pass
    return editor 

## Not being used atm
#def checkInModule(params):
#    try:
#        path = params['path']
#        module_id = path[1]
#        module = Module.objects.get()
#    except:
#        pass
#
#def createModule(text, metadata, attachment, client_id):
#    """ Extract info from params and put into new module 
#        This one doens't return API result, only Module object
#    """
#    module = None
#    try:
#        module = models.Material.objects.create(
#            text       = text, 
#            metadata   = metadata,
#            attachment = attachment,
#            client_id  = client_id
#            )
#        module.save()
#    except:
#        raise
#    return module
#
#def deleteModule(request):
#    """ 
#    """
#    pass
#
#
#def downloadModule(request):
#    """ 
#    """
#    pass
#
#
#def getModuleMetadata(request):
#    """ 
#    """
#    pass


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

    def list(self, request, *args, **kwargs):
        """ Customized function for listing materials with same ID
        """
        try: 
            m_objects = self.model.objects
            if kwargs.get('mid', None):
                self.object_list = m_objects.filter(material_id=kwargs['mid'])
            else:
                self.object_list = m_objects.all()
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

class MaterialDetail(generics.RetrieveUpdateDestroyAPIView):
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
                object = object.filter(**args).order_by('version').reverse()[0]
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

