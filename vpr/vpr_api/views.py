# Create your views here.

from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseNotAllowed
from django.core import urlresolvers
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable
from rest_framework import status
from datetime import datetime, timedelta
import md5 
import re
import time

from vpr_api.serializers import UserSerializer, GroupSerializer
from vpr_api.models import APIClient as Client
from vpr_api.models import APIToken as Token
from vpr_api.models import generateClientKey, generateClientID


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'authors': reverse('author-list', request=request),
        'editors': reverse('editor-list', request=request),
        'categories': reverse('category-list', request=request),
        'materials': reverse('material-list', request=request),
#        'search': reverse('general-search', request=request),
    })



@api_view(['GET', 'POST'])
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
        ip = request.META.get('REMOTE_ADDR', '')
        comb = inputs['comb']
        sugar = inputs['sugar']
        cid = cid.strip().lower()
        res = {'client_id': cid}

        client = verifyAuthComb(cid, comb, sugar)
        if client:
            token = createToken(client, ip)
            res['token'] = token.token
            res['expire'] = token.expire
            res['result'] = 'OK'
        else:
            raise NotAcceptable('Authentication failed (invalid combination)')
            # or...
            #return Response({'details':'Authentication ...'}, status=406)
    except:
        raise
        res['result'] = 'ERROR'
        res['error'] = 'Error when authenticating API client'

    return Response(res)


def createToken(client, ip='1.1.1.1'):
    """Create the token and save into DB with given client object"""
    token = Token(client=client,
                  client_ip=ip,
                  )
    expire = datetime.now() + timedelta(minutes=30)
    token.expire = expire.isoformat()
    token.token = md5.md5(client.client_id + token.expire).hexdigest()
    token.save()
    return token
 

def createAuthCombination(secret, sugar):
    """Returns the good combination from secret key and sugar"""
    return md5.md5(secret + sugar).hexdigest()


def verifyAuthComb(cid, comb, sugar):
    """ Verify sent info for authenticating
    """
    try:
        if comb == '' or sugar == '':
            raise
        client = Client.objects.get(client_id=cid)
        good_comb = createAuthCombination(client.secret_key, sugar)
        print 'GOOD COMB: ' + good_comb
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
    try:
        token = getActiveToken(client_id)
        token = token.token
    except AttributeError: 
        token = '#'
    return post_token == token


@api_view(['GET'])
def testTokenView(request, token):
    """Check if the given token and client_id are correct"""
    client_id = request.GET.get('cid', '')
    if validateToken(client_id, token):
        return Response({'details':'Valid token'}, status=status.HTTP_200_OK)
    return Response({'details':'Invalid token'}, 
                    status=status.HTTP_401_UNAUTHORIZED)


def getTokenView(request, cid):
    """(dev) Returns the token of given client ID"""
    client = Client.objects.get(client_id=cid)
    token = createToken(client)
    return HttpResponse(cid + '<br>' + token.token)


REGISTER_DELAY = 0

@api_view(['GET', 'POST'])
def registerClient(request):
    """This is for the installation process of VPW. Email is mandatory and used
       to check the unique of the remote system. Both email and name could be 
       sent through POST or GET.
            email    email of the client (required and unique)
            name     name of the client (required).
    """
    try:
        time.sleep(REGISTER_DELAY)   # dirty way to reduce multiple request
        email = request.GET.get('email', '') or request.POST.get('email', '')  
        name = request.GET.get('name', '') or request.POST.get('name', '')  
        # not allow same client ID or reusing
        if not email or not name or Client.objects.filter(email=email):
            response = Response({}, status=status.HTTP_400_BAD_REQUEST)
        else:
            client_id = generateClientID(request.META.get('REMOTE_ADDR', ''))
            client = Client(client_id = client_id,
                            name = name,
                            email = email,
                            secret_key = generateClientKey(email or 'empty')
                            )
            client.save()
            response = Response({'client_id': client_id,
                                'secret': client.secret_key
                                },
                                status=status.HTTP_201_CREATED)
        return response
    except:
        raise
