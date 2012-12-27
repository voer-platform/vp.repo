# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from rest_framework.response import Response
from hashlib import md5
from datetime import datetime

from models import Module

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
    """
    path = path.split('/')
    path = [item for item in path if len(item)>0]
    return path


def checkInModule(params):
    """ 
    """
    try:
        path = params['path']
        module_id = path[1]
        module = Module.objects.get()
    except:
        pass


def createModule(params):
    """ Extract info from params and put into new module 
    """
    module_id = ''
    try:
        module = Module()
        module.text = params['text']
        module.version = '1'
        module.save()
        module_id = generateModuleId()
    except:
        pass
    return Response({'module':{
                        'id': module_id,
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
