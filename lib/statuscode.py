import os, sys

class rtnCode:
    SUCCEED = 0
    TESTFAILED = -1
    SCRIPTFAILED = -2
    ENVFAILED = -3
    TIMEOUT = -9
    
    REBOOT = 10
    
class signalCode:
    SIGHUP = 1
    SIGINT = 2
    SIGTERM = 15
    SIGSTOP = 19
    
class logLevelCode:
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30 
    ERROR = 40
    CRITICAL = 50 

