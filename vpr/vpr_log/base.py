
class BaseLogHandler():

    def saveLog(self, record):
        """ Store log record into FS or Database """
        pass

    def getLog(self):
        """ Retrieve and return log entry(ies) from DB """
        pass    

    def clean(self, period=30):
        """ Clean all log records older than period days """
        pass
        
