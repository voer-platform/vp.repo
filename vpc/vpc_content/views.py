# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
# from rest_framework.response import Response


def dispatchModuleCalls(request):
    """ Analyze the requests and call the appropriate function
    """
    # analyze the URL
    path = request.path.split('/')
    path = [item for item in path if len(item)>0]
    if request.method == 'POST':
        if len(path) > 1:
            checkInModule(request)
        else:
            createModule(request)
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


def checkInModule():
    """ 
    """
    pass


def createModule():
    """ 
    """
    pass


def deleteModule():
    """ 
    """
    pass


def downloadModule():
    """ 
    """
    pass


def getModuleMetadata():
    """ 
    """
    pass
