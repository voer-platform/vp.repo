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


def checkInModule(params):
    """ 
    """
    try:
        path = params['path']
        module_id = path[1]
        module = Module.objects.get()
    except:
        pass

def createModule(text, metadata, attachment, client_id):
    """ Extract info from params and put into new module 
        This one doens't return API result, only Module object
    """
    module = None
    try:
        module = models.Module.objects.create(
            text       = text, 
            metadata   = metadata,
            attachment = attachment,
            client_id  = client_id
            )
        module.save()
    except:
        raise
    return module

def deleteModule(request):
    """ 
    """
    pass


def downloadModule(request):
    """ 
    """
    pass


def getModuleMetadata(request):
    """ 
    """
    pass


# CATEGORY CALLS

class CategoryList(generics.ListCreateAPIView):
    """docstring for AuthorList"""
    model = models.Category
    serializer_class = serializers.CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for CategoryDetail"""

    model = models.Category
    serializer_class = serializers.CategorySerializer
    #def get_object(self, id):
    #    try:
    #        return models.Category.objects.get(id=id)
    #    except models.Category.DoesNotExist:
    #        raise Http404
    #    
    #def get(self, request, pk, format=None):
    #    category = self.get_object(pk)
    #    sr = serializers.CategorySerializer(category)
    #    return Response(sr.data)


# EDITOR CALLS

class EditorList(generics.ListCreateAPIView):
    """docstring for EditorList"""
    model = models.Editor
    serializer_class = serializers.EditorSerializer


class EditorDetail(generics.ListCreateAPIView):
    """docstring for EditorDetail"""

    def get_object(self, category_id):
        try:
            return models.Editor.objects.get(id=editor_id)
        except models.Editor.DoesNotExist:
            raise Http404
        
    def get(self, request, editor_id, format=None):
        edtior = self.get_object(editor_id)
        sr = serializers.EditorSerializer(editor)
        return Response(sr.data)



# AUTHOR CALLS

class AuthorList(generics.ListCreateAPIView):
    """docstring for AuthorList"""
    model = models.Author
    serializer_class = serializers.AuthorSerializer


class AuthorDetail(generics.ListCreateAPIView):
    """docstring for AuthorDetail"""

    def get_object(self, author_id):
        try:
            return models.Author.objects.get(author_id=author_id)
        except models.Author.DoesNotExist:
            raise Http404
        
    def get(self, request, author_id, format=None):
        author = self.get_object(author_id)
        sr = serializers.AuthorSerializer(author)
        return Response(sr.data)

# OLD CLASS BASED ON APIVIEW
#class ModuleList(APIView):
class ModuleList(generics.ListCreateAPIView):
    """
    Return list of modules or create a new one
    """
    model = models.Module
    serializer_class = serializers.ModuleSerializer

    #def get(self, request, format=None):
    #    """docstring for get"""
    #    modules = models.Module.objects.all()
    #    sr = serializers.ModuleSerializer(modules)
    #    return Response(sr.data)

    def post(self, request, format=None):
        """docstring for post"""
        return Response(request.DATA)
        #sr = serializers.ModuleSerializer(data=request.DATA)
        #if sr.is_valid():
        #    sr.save()
        #    return Response(sr.data, status=status.HTTP_201_CREATED)
        #return Response(sr.errors, status=status.HTTP_400_BAD_REQUEST)



class ModuleDetail(APIView):
    """
    Return module data, update/check-in it or delete it
    """

    def get_object(self, module_id):
        try:
            return models.Module.objects.get(module_id=module_id)     
        except models.Module.DoesNotExist:
            raise Http404

    def get(self, request, module_id, format=None):
        module = self.get_object(module_id)
        sr = serializers.ModuleSerializer(module)
        return Reponse(sr.data)
