import logging
#from utils import saveLog


# not being used for now
class DatabaseHandler(logging.Handler):
    """ """
    
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        pass
        

