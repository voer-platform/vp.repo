from rest_framework.response import Response
from django.conf import settings
from django.utils.log import getLogger
from django.http import HttpRequest
from datetime import datetime

from vpr_api.views import validateToken
from vpr_api.utils import COOKIE_CLIENT, COOKIE_TOKEN
from vpr_api.models import APIRecord
from vpr_api.signals import after_apicall


logger = getLogger('vpr.api.request')

CLIENT_ID_UNKNOWN = -1
LOG_CHECK_TOKEN = 'Check API token (%s): %s'
LOG_RECORD_FAILED = 'Recording API log failed'


def isRequest(obj):
    """ Check if the obj is true HttpRequest or not
    """
    return isinstance(obj, HttpRequest)


def getRequest(*args):
    """ Find and return true request object from arguments
    """
    request = None
    if len(args) > 1:
        if hasattr(args[1], '_request'):
            request = args[1]._request
    elif isRequest(args[0]):
        request = args[0]
    elif hasattr(args[0], '_request'):
        request = args[0]._request
    return request
    

def api_token_required(func):
    """docstring for TokenValidator"""
        
    def wrappee(*args, **kwargs):
        """Check if the token is valid or not, in order to process the request"""
        request = getRequest(*args)
        if settings.TOKEN_REQUIRED == False:
            logger.info('API authentication bypassed')
            return func(*args, **kwargs)

        token = request.COOKIES.get(COOKIE_TOKEN, None)
        client_id = request.COOKIES.get(COOKIE_CLIENT, None)

        # 2nd option, extracting from GET query
        if not token or not client_id:
            token = request.GET.get(COOKIE_TOKEN, None)
            client_id = request.GET.get(COOKIE_CLIENT, None)
        if validateToken(client_id, token):
            logger.info(LOG_CHECK_TOKEN % (client_id, 'OK'))
            return func(*args, **kwargs)
        else:
            logger.info(LOG_CHECK_TOKEN % (client_id, 'KO'))
            return Response({'details':'Permission denied due to invalid API token'},
                            status=401);
    return wrappee


def api_log(func):
    """Record all API calls"""
    
    def wrappee(*args, **kwargs):
        """ """
        return func(*args, **kwargs)

        res = func(*args, **kwargs)  
        try:
            request = getRequest(*args)
            client_id = request.COOKIES.get(COOKIE_CLIENT)
            if not client_id:
                client_id = request.GET.get(COOKIE_CLIENT, CLIENT_ID_UNKNOWN)
            qr_keys = request.GET.keys()
            path = '/'.join(request.path.split('/')[2:])
            query = '&'.join([k+'='+request.GET.get(k,'') for k in qr_keys])
            after_apicall.send(sender=None, request=request, result=res.status_code)
        except:
            logger.error(LOG_RECORD_FAILED)
        return res     

    return wrappee
