from datetime import datetime, timedelta
from vpr_api.models import APIRecord

LIMIT_TIME_RANGE = 31*24

class APIRecordStats(object):   
    __time_start = None
    __time_end = None
    __period = None
    __path = ''
    __method = ''
    __query = ''

    def __init__(self, time_end, period=72, rpath='', rmethod='', rquery='', rclient=None):
        """ """
        if period > LIMIT_TIME_RANGE:
            period = 72
        self.__time_start = time_end - timedelta(hours=period)
        self.__time_end = time_end
        self.__period = period

    def countResult(self, t_start=None, t_end=None):
        """ """
        if t_start == None or t_end == None:
            t_start = self.__time_start
            t_end = self.__time_end

        params = {
            'time__gte': t_start,
            'time__lte': t_end,
            }

        if self.__path:
            params['path__contains'] = self.__path
        if self.__query:
            params['query__contains'] = self.__query
        if self.__method:
            params['type'] = self.__method

        print params

        return APIRecord.objects.filter(**params).count()


    def getPeriodResults(self, period_number=10):
        """Split the whole time into specific periods and get their values"""
        t0 = datetime.now()
        time_step = timedelta(hours=round(self.__period/period_number))
        time_cursor = self.__time_start
        results = []
        for _ in range(period_number-1):
            results.append(self.countResult(time_cursor, time_cursor+time_step))
            time_cursor += time_step
        results.append(self.countResult(time_cursor, self.__time_end))
        
        print 'Elapsed time: ', datetime.now()-t0
        return results

