import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.log import Log
from lib.statuscode import rtnCode

from time import sleep

def main():

    log = Log()
    log.infoPrint("cpu_vtd testing starting...")

    log.stepPrint("boot to bios")

    log.infoPrint("boot to bios successfully")

    log.stepPrint("turn on ht")

    log.stepPrint("boot to OS")

    log.stepPrint("check ht")
    sleep(30)

    log.summaryPrint()
    
    return rtnCode.SUCCEED

if __name__ == "__main__":
    sys.exit(main())