# Create your views here.

from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.core import urlresolvers
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from datetime import datetime
import md5 
import re

from vpc_api.serializers import UserSerializer, GroupSerializer
from vpc_api.models import APIClient as Client
from vpc_api.models import APIToken as Token


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
#        'users': reverse('user-list', request=request),
#        'groups': reverse('group-list', request=request),
#        'auth': reverse('authenticate'),
#        'token': reverse('test-token', request=request),
        'authors': reverse('author-list', request=request),
        'editors': reverse('editor-list', request=request),
        'categories': reverse('category-list', request=request),
        'materials': reverse('material-list', request=request),
#        'search': reverse('general-search', request=request),
    })


class UserList(generics.ListCreateAPIView):
    """
    API endpoint that represents a list of users.
    """
    model = User
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that represents a single user.
    """
    model = User
    serializer_class = UserSerializer


class GroupList(generics.ListCreateAPIView):
    """
    API endpoint that represents a list of groups.
    """
    model = Group
    serializer_class = GroupSerializer


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that represents a single group.
    """
    model = Group
    serializer_class = GroupSerializer


@api_view(['GET'])
def authenticate(request, cid):
    """
    Authenticate a client and issue session token
    """
    res = {}
    try:
        if request.method == 'POST':
            inputs = request.POST
        elif request.method == 'GET':
            inputs = request.GET
        comb = inputs['comb']
        sugar = inputs['sugar']
        cid = cid.strip().lower()
        res = {'client_id': cid}

        client = verifyAuthComb(cid, comb, sugar)
        if client:
            token = Token(client = client,
                          client_ip = '192.168.1.1',
                          )
            token.expire = datetime.now().isoformat()
            token.token = md5.md5(cid + token.expire).hexdigest()
            token.save()
            res['token'] = token.token
            res['expire'] = token.expire
            res['result'] = 'OK'
    except:
        raise
        res['result'] = 'ERROR'
        res['error'] = 'Error when authenticating API client'

    return Response(res)


def verifyAuthComb(cid, comb, sugar):
    """ Verify sent info for authenticating
    """
    try:
        if comb == '' or sugar == '':
            raise
        client = Client.objects.get(client_id=cid)
        good_comb = md5.md5(client.secret_key + sugar).hexdigest()
        print "GOOD COMB: " + good_comb
        if good_comb != comb:
            raise            
    except:
        return None
    return client


def getActiveToken(cid):
    """ Retrieve and return the current active token of a specified token
        Only the newest token is returned.
    """
    token = None
    try:
        client = Client.objects.get(client_id=cid)
        # clear dead tokens
        cleanOldTokens(client) 
        # then get the newest
        token = Token.objects.filter(client=client).order_by('expire').reverse()[0]
    except:
        token = "ERROR: when retrieving active token" 
    return token


def cleanOldTokens(client):
    """ Delete all old tokens, only keep 2 newest one.
        argument is a client object
    """
    try:
        tokens = Token.objects.filter(client=client).order_by('expire').reverse()[2:]
        [ tk.delete() for tk in tokens ]
    except:
        msg = "Error when deleting old tokens"
        return None
    return len(tokens)
    

def getRequestVersion(request):
    """ This function analizes and returns the version of called API
        NOT BEING USED ATM.
    """
    version = ''
    #url = request.build_absolute_uri()
    re_version = re.compile('^/[0-9]*(\.[0-9]+)?')
    try:
        version = re_version.search(request.path).group()[1:]
    except:
        pass
    return version


def validateToken(client_id, post_token):
    """ Verify if the transfered token and client ID is matched and valid
    """
    token = getActiveToken(request, client_id)
    return post_token == token


# TESTING FUNCTIONS ======================================== 


def testActiveToken(request, cid):
    """ Just for testing 
    """
    msg = 'API version: ' + getRequestVersion(request) + '<br/>'
    msg += str(getActiveToken(cid))
    return HttpResponse(msg) 



