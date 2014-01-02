from datetime import datetime
from django.dispatch import receiver
from django.conf import settings 

from vpr_log.logger import Logger
from signals import after_apicall


logger = Logger() 

LOG_ERROR_RECORDING = 'Unknown error occurs when recording API request'
CLIENT_ID_UNKNOWN = -1


@receiver(after_apicall)
def handle_apicall(sender, **kwargs):
    """Handle of API call signal. This does two things:
        1. Send an update to statsd
        2. Store a log record into DB
    """
    request = kwargs['request']
    logger.apilog(kwargs.get('result', None), request)

