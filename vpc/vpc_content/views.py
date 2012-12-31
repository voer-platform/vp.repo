# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from rest_framework.response import Response
from hashlib import md5
from datetime import datetime

import models

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


def createModule(text, meta, attachment, client_id):
    """ Extract info from params and put into new module 
    """
    try:
        module = Module.objects.create(
            text       = text, 
            metadata   = meta,
            attachment = attachment,
            client_id  = client_id
            )
        module.save()
    except:
        pass
    return Response({'module':{
                        'id': module.module_id,
                        'title': params.title
                        }
                    })



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
