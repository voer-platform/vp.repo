from rest_framework.response import Response
from django.conf import settings
from django.utils.log import getLogger
from django.http import HttpRequest, Http404
from datetime import datetime

from vpr_api.views import validateToken
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

        token = request.COOKIES.get(settings.VPR_COOKIE_TOKEN, None)
        client_id = request.COOKIES.get(settings.VPR_COOKIE_CLIENT, None)

        # 2nd option, extracting from GET query
        if not token or not client_id:
            token = request.GET.get(settings.VPR_COOKIE_TOKEN, None)
            client_id = request.GET.get(settings.VPR_COOKIE_CLIENT, None)
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
        try:
            res = func(*args, **kwargs)  
            s_code = res.status_code
        except Http404:
            s_code = 404 

        # 404, still fire the signal
        request = getRequest(*args)
        after_apicall.send(sender=None, request=request, result=s_code)

        if s_code == 404:
            raise Http404
        return res

    return wrappee
