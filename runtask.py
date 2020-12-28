import json
import os
import logging
from datetime import datetime 
import argparse
from time import sleep

def main():
    parser = argparse.ArgumentParser(description="Utility For Test Execution")
    parser.add_argument('-D','--testrundir', default='', required=True, help='TestRun Directory')
    parser.add_argument('-I','--testrunid', default='', required=False, help='TestRun ID')
    parser.add_argument('-i','--testinstanceid', default='', required=True, help='TestInstance ID')
    parser.add_argument('-S','--suts', default='[]', required=False, help='SUTs provided to launch test')
    parser.add_argument('-T','--timeout', default=7200, required=False, help='timeout value for testing, unit in seconds')
    parser.add_argument('-s','--interpreter', default='python36', required=True, help='Script interpreter, default is python36')
    parser.add_argument('-t','--script', default='', required=False, help='Whole Script path')
    parser.add_argument('-p','--scriptparams', default='{}',required=False, help='Script Parameters to be tested')
    parser.add_argument('-F','--testruningstatfile', default='{}',required=False, help='testrunning stat file')

    args = parser.parse_args()
    
    