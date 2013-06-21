from rest_framework.response import Response
from django.conf import settings
import logging

from vpr_api.views import validateToken
from vpr_api.utils import COOKIE_CLIENT, COOKIE_TOKEN
from vpr_log.logger import get_logger


logger = get_logger('api')

LOG_CHECK_TOKEN = 'Check API token (%s): %s'

def api_token_required(func):
    """docstring for TokenValidator"""
        
    def wrappee(*args, **kwargs):
        """Check if the token is valid or not, in order to process the request"""

        if settings.TOKEN_REQUIRED == False:
            logger.info('API authentication bypassed')
            return func(*args, **kwargs)

        request = args[1]._request
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
