from datetime import datetime

from django.dispatch import receiver
from django.utils.log import getLogger

from models import APIRecord 
from signals import after_apicall


logger = getLogger('vpr.api.request')

# Logs, records

LOG_ERROR_RECORDING = 'Unknown error occurs when recording API request'

# Constants

COOKIE_TOKEN = 'vpr_token'
COOKIE_CLIENT = 'vpr_client'
CLIENT_ID_UNKNOWN = -1

logger = getLogger('vpr.api.requests')

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
                client_id = request.GET.get(COOKIE_CLIENT, CLIENT_ID_UNKNOWN)
            qr_keys = request.GET.keys()
            query = '&'.join([k+'='+request.GET.get(k,'') for k in qr_keys])
            rec = APIRecord(
                client_id = client_id,
                method = request.method,
                path = request.path,
                time = datetime.now(),
                result = code,
                query = query,
                )
            #rec.ip = request.META.get('REMOTE_ADDR', ''),
            rec.save()
        except:
            logger.error(LOG_ERROR_RECORDING)
            

@receiver(after_apicall)
def handle_apicall(sender, **kwargs):
    """Handle of API call signal. This does two things:
        1. Send an update to statsd
        2. Store a log record into DB
    """
    logger.info('Hello there')


