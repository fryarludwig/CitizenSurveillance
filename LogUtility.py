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
            if isinstance(message, list):
                for part in message:
                    self.write(self.str_error.format(part))
            elif isinstance(message, dict):
                for key, value in message.iteritems():
                    self.write(self.str_error.format(key + ": " + value))
            else:
                self.write(self.str_error.format(message))

    def Warn(self, message):
        if self.show_warn:
            if isinstance(message, list):
                for part in message:
                    self.write(self.str_warn.format(part))
            elif isinstance(message, dict):
                for key, value in message.iteritems():
                    self.write(self.str_warn.format(key + ": " + value))
            else:
                self.write(self.str_warn.format(message))

    def Info(self, message):
        if self.show_info:
            if isinstance(message, list):
                for part in message:
                    self.write(self.str_trace.format(part))
            elif isinstance(message, dict):
                for key, value in message.iteritems():
                    self.write(self.str_trace.format("Key " + str(key) + " has value: " + str(value)))
            else:
                self.write(self.str_trace.format(message))

    def Trace(self, message):
        if self.show_trace:
            if isinstance(message, list):
                for part in message:
                    self.write(self.str_trace.format(part))
            elif isinstance(message, dict):
                for key, value in message.iteritems():
                    self.write(self.str_trace.format(key + ": " + value))
            else:
                self.write(self.str_trace.format(message))
