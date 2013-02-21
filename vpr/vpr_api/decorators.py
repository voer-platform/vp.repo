from rest_framework.response import Response
from vpr_api.views import validateToken


def api_token_required(orig):
    """Check if the token is valid or not, in order to process the request"""
    def checkTokenFirst(*args, **kwargs):
        # check API token inside cookies
        try:
            print 'API token checking'
            request = args[1]._request
            token = request.COOKIES.get('vpr_token', '')
            client_id = request.COOKIES.get('vpr_client_id', '')
            if validateToken(client_id, token):
                return orig(*args, **kwargs)
            else:
                return Response({'details':'Permission denied due to invalid API token'},
                                status=401);
        except:
            raise
            return Response({'details':'API request processing failed due to unknown reason'},
                            status=404);

    return checkTokenFirst

