import logging

vpr_loggers = {'api': 'vpr.api',
           'content': 'vpr.content',
           'system': 'vpr.system',
           'dashboard': 'vpr.dashboard',
           'root': 'vpr.root'
           }


class DatabaseHandler(logging.Handler):
    """ """
    
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        print 'What is going on here?'


