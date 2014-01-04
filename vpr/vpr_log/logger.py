from datetime import datetime
from django.conf import settings
from django.utils import importlib

from config import * 


CLIENT_ID_UNKNOWN = -1


class LogBase(object):
    path = ''
    code = None
    message = ''
    logset = None

    def __init__(self, **kwargs):
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
        self.time = datetime.utcnow()


class APILog(LogBase):
    """ Storing basic information of a lob record 
    """
    client_id = None
    method = None
    query = None
    ip = None
    data = None


class NormalLog(LogBase):
    """ General purpose log
    """
    pass


class Logger():
    """ General logger for VPR
    """
    def __init__(self):
        LogHandler = get_class(settings.VPR_LOG_HANDLER)
        try:
            self.handler = LogHandler()
        except:
            # OK, let it be
            pass
       
    def error(self, message, path=''):   
        code = VPR_ERROR 
        self.save_log(code, message, path)

    def info(self, message, path=''):
        code = VPR_INFO
        self.save_log(code, message, path)

    def debug(self, message, path=''):
        code = VPR_DEBUG
        self.save_log(code, message, path)

    def warn(self, message, path=''):
        code = VPR_WARNING
        self.save_log(code, message, path)

    def save_log(self, code, message, path):
        """ Save log from general event of system 
        """
        record = NormalLog(code=code, message=message, path=path)
        record.logset = settings.VPR_LOG_SETS['default']
        self.push(record)

    def apilog(self, code, request):
        """ Save log from API call and result
        """
        client_id = request.COOKIES.get(settings.VPR_COOKIE_CLIENT)
        if not client_id:
            client_id = request.GET.get(
                settings.VPR_COOKIE_CLIENT, 
                CLIENT_ID_UNKNOWN)
        qr_keys = request.GET.keys()
        query = '&'.join([k+'='+request.GET.get(k,'') for k in qr_keys])
        values = { 
            'client_id': client_id,
            'method': request.method,
            'path': request.path,
            'code': code,
            'query': query,
            'ip': request.META.get('REMOTE_ADDR', ''),
            }
        if request.method == 'POST' and code >= 400:
            values['data'] = request.POST.dict() 
        record = APILog(**values)
        record.logset = settings.VPR_LOG_SETS['api']
        self.push(record)
    
    def push(self, record):
        """ Really push the log record into DB
        """
        try:
            self.handler.store(record)
        except:
            # should be something here
            pass 

def get_class(path):
    """ Returns the class specified in path 
    """
    module_path = path.split('.')
    class_name = module_path.pop()
    module_path = '.'.join(module_path)
    module = importlib.import_module(module_path)
    
    if not hasattr(module, class_name):
        raise ImportError("Module %s doesn't have class named: %s" %
            (module_path, class_name))
    
    return getattr(module, class_name)
