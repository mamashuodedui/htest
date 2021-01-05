import logging
import sys
from math import log10, floor

class Log:
    def __init__( self, name=None, logfile=None, level=None ):
        if name is None:
            self.name = "DefaultTestLogger"
        else:
            self.name = name
        if logfile is None:
            self.logfile = 'defaulttest.log'
        else:
            self.logfile = logfile
        if level is None:
            self.level = 'INFO'
        else:
            self.level = level
        loglevel = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        
        formatter = ('[%(asctime)s][%(levelname)s]%(message)s')

        # Define basic configuration
        logging.basicConfig(
            # Define logging level
            level=loglevel[self.level],
            # Declare the object we created to format the log messages
            format=formatter,
            # Declare handlers
            handlers=[
                logging.FileHandler(self.logfile),
                logging.StreamHandler(sys.stdout),
            ]
        )
        self.logger = logging.getLogger(name)
        
        #test stuff
        self.step = 0
        self.failsteps = []
        self.result = "SUCCEED"
        
    def msgPrint(self, level, msg):
        if level == 'DEBUG':
            self.logger.debug(msg)
        if level == 'INFO':
            self.logger.info(msg)
        if level == 'WARNING':
            self.logger.warning(msg)
        if level == 'ERROR':
            self.logger.error(msg)
        if level == 'CRITICAL':
            self.logger.critical(msg)

    def debugPrint(self, msg):
        self.msgPrint(level="DEBUG", msg=msg)

    def infoPrint(self, msg):
        self.msgPrint(level="INFO", msg=msg)

    def warningPrint(self, msg):
        self.msgPrint(level="WARNING", msg=msg)

    def errorPrint(self, msg):
        self.msgPrint(level="ERROR", msg=msg)
        self.failsteps.append({"step":self.step, "msg":"ERROR: " + msg})
        
    def criticalPrint(self, msg):
        self.msgPrint(level="CRITICAL", msg=msg)
        self.failsteps.append({"step":self.step, "msg":"CRITICAL: " + msg})

    def summaryPrint(self):
        self.msgPrint(level="INFO", msg = "$"*88)
        self.msgPrint(level="INFO", msg = "$"*88)
        if len(self.failsteps) == 0:
            self.msgPrint(level="INFO", msg = "$" +  "Test Finished, ALL Are SUCCEED" + " " * 56 + "$")
        else:
            self.msgPrint(level="INFO", msg = "$" + "Test Finished, Failed STEPS Are:" + " " * 54 + "$")
            for i in range(len(self.failsteps)):
                self.msgPrint(level="INFO", msg = '#STEP' + "0" * (2 - floor(log10(self.failsteps[i]['step']))) + str(self.failsteps[i]['step']) + " " * 79 + "#")            
                if int(len(self.failsteps[i]['msg'])/86) == 0:
                    self.msgPrint(level="INFO", msg = "#" + self.failsteps[i]['msg'][:len(self.failsteps[i]['msg'])%86] + " " * (86-len(self.failsteps[i]['msg'])%86) + "#")
                else:
                    counter = 0
                    for i in range(int(len(self.failsteps[i]['msg'])/86)):
                        self.msgPrint(level="INFO", msg = "#" + self.failsteps[i]['msg'][86*i:86*(i+1)] + "#")
                        counter += 1
                    self.msgPrint(level="INFO", msg = "#" + self.failsteps[i]['msg'][86 * counter: 86 * counter + len(self.failsteps[i]['msg'])%86] + " " * (86-len(self.failsteps[i]['msg'])%86) + "#")
                self.msgPrint(level="INFO", msg = "#"*88)
    
        self.msgPrint(level="INFO", msg = "$"*88)
        self.msgPrint(level="INFO", msg = "$"*88)

    def stepPrint(self, msg, step=None):
        if step is None:
            self.step += 1
        else:
            self.step = step
        self.msgPrint(level="INFO", msg = "#"*88)
        self.msgPrint(level="INFO", msg = '#STEP' + "0" * (2 - floor(log10(self.step))) + str(self.step) + " " * 79 + "#")            
        if int(len(msg)/86) == 0:
            self.msgPrint(level="INFO", msg = "#" + msg[:len(msg)%86] + " " * (86-len(msg)%86) + "#")
        else:
            counter = 0
            for i in range(int(len(msg)/86)):
                self.msgPrint(level="INFO", msg = "#" + msg[86*i:86*(i+1)] + "#")
                counter += 1
            self.msgPrint(level="INFO", msg = "#" + msg[86 * counter: 86 * counter + len(msg)%86] + " " * (86-len(msg)%86) + "#")
        self.msgPrint(level="INFO", msg = "#"*88)

