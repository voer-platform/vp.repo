import logging

vpr_loggers = {'api': 'vpr.api',
           'content': 'vpr.content',
           'system': 'vpr.system',
           'dashboard': 'vpr.dashboard',
           'root': 'vpr.root'
           }


class Logger(logging.Logger):
    """Customized logger of VPR"""
    pass        


def get_logger(name='root'):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    return Logger.manager.getLogger(vpr_loggers[name])

