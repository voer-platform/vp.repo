from rest_framework.response import Response
from vpr_api.views import validateToken

COOKIE_TOKEN = 'vpr_token'
COOKIE_CLIENT = 'vpr_client'

def api_token_required(orig):
    """Check if the token is valid or not, in order to process the request"""
    def checkTokenFirst(*args, **kwargs):
        # check API token inside cookies
        try:
            request = args[1]._request
            token = request.COOKIES.get(COOKIE_TOKEN, None)
            client_id = request.COOKIES.get(COOKIE_CLIENT, None)
            # 2nd option, extracting from GET query
            if not token or not client_id:
                token = request.GET.get(COOKIE_TOKEN, None)
                client_id = request.GET.get(COOKIE_CLIENT, None)
            if validateToken(client_id, token):
                return orig(*args, **kwargs)
            else:
                return Response({'details':'Permission denied due to invalid API token'},
                                status=401);
        except:
            return Response({'details':'API request processing failed due to unknown reason'},
                            status=404);

    return checkTokenFirst

