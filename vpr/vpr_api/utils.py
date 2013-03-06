from datetime import datetime

from vpr_api.models import APIRecord 
from vpr_log.logger import get_logger

# Logs, records

LOG_ERROR_RECORDING = 'Unknown error occurs when recording API request'

# Constants

COOKIE_TOKEN = 'vpr_token'
COOKIE_CLIENT = 'vpr_client'

logger = get_logger('api')


class APILogger():
    """Provides methods for recording API activities"""

    def cleanExpired(self):
        """docstring for cleanExpired"""
        pass

    def export(self):
        """docstring for exportLog"""
        pass

    def record(self, request, code=0):
        """Collects info from API action and saves into DB
                request - HttpRequest
                code - returned code of the API call 
        """
        try:
            client_id = request.COOKIES.get(COOKIE_CLIENT)
            if not client_id:
                client_id = request.GET.get(COOKIE_CLIENT)
            rec = APIRecord()
            rec.client_id = client_id
            rec.method = request.method
            rec.path = request.path
            rec.time = datetime.now()
            rec.ip = request.META.get('REMOTE_ADDR', '')
            rec.result = code
            rec.save()
        except:
            logger.error(LOG_ERROR_RECORDING)
            
