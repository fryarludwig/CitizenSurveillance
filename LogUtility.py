import os
import pprint
import datetime
import sys

CURRENT_TIME = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M')
LOGFILE_PATH = '{}-log.txt'.format(CURRENT_TIME)

class LogUtility(object):
    """
    Overrides Python print function and maintains the program log file
    """
    def  __init__(self, logfile=None, overwrite=False):
        self.str_error = "[ERROR] - {}\n"
        self.str_warn  = "[WARN]  - {}\n"
        self.str_info  = "[INFO]  - {}\n"
        self.str_trace = "[TRACE] - {}\n"
        self.show_error = True
        self.show_warn = True
        self.show_info = True
        self.show_trace = True

        self.terminal = sys.stdout

        if logfile is not None:
            if overwrite or not os.path.exists(logfile):
                mode = 'w'
            else:
                mode = 'a'
            self.log = open(logfile, mode=mode)
        else:
            self.log = None

    def write(self, message):
        self.terminal.write(message)
        if self.log is not None:
            self.log.write(message)

    def Error(self, message):
        if self.show_error:

            self.write(self.str_error.format(pprint.pformat(message)))

    def Warn(self, message):
        if self.show_warn:

            self.write(self.str_warn.format(pprint.pformat(message)))

    def Info(self, message):
        if self.show_info:
            self.write(self.str_info.format(pprint.pformat(message)))

    def Trace(self, message):
        if self.show_trace:
            self.write(self.str_trace.format(pprint.pformat(message)))
