import json
import os
from datetime import datetime, timedelta
import argparse
import subprocess
import shutil
#import psutil

import sys
sys.path.append(".")

from lib.statuscode import rtnCode

def main():
    parser = argparse.ArgumentParser(description="Utility For Test Execution")
    parser.add_argument('-D','--testrundir', default='', required=True, help='TestRun Directory')
    parser.add_argument('-I','--testrunid', default='', required=False, help='TestRun ID')
    parser.add_argument('-i','--testinstanceid', default='', required=True, help='TestInstance ID')
    parser.add_argument('-S','--suts', default='[]', required=True, help='SUTs provided to launch test')
    parser.add_argument('-o','--timeout', default=7200, required=False, help='timeout value for testing, unit in seconds')
    parser.add_argument('-s','--interpreter', default='python36', required=True, help='Script interpreter, default is python')
    parser.add_argument('-t','--script', default='', required=True, help='Whole Script path')
    parser.add_argument('-p','--scriptparams', default='{}',required=False, help='Script Parameters to be tested')
    parser.add_argument('-F','--testruningstatfile', default='',required=True, help='testrunning stat file')
    parser.add_argument('-O','--owner', default='admin',required=True, help='test owner')

    args = parser.parse_args()
    
    print("Check Test Environment")
    if not os.path.ismount('/testdata'):
        return rtnCode.ENVFAILED
    
    print("Create testresult directory")
    t = datetime.now()
    starttime = t
    testinstance_dir = "_".join([os.path.basename(args.script).split('.')[0], str(t.year), str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second), str(t.microsecond)])
    os.mkdir(testinstance_dir)
    os.chdir(testinstance_dir)

    print("Copy Template File to testresult directory")
    shutil.copyfile('../htest/templates/testresult_summary.html','testresult_summary.html')

    print("Parsing testing data")
    with open('/testdata/TEST_RUNNING_STAT/' + args.testruningstatfile, 'r') as fh:
        testrunningdata = json.load(fh)

    if str(args.interpreter).lower() == 'shell':
        cmd = 'source ../htest/venv/bin/activate && sh ../%s %s'%(args.script, args.scriptparams)
    elif str(args.interpreter).lower() == 'python':
        cmd = 'source ../htest/venv/bin/activate && /opt/python/python36/bin/python36 ../%s %s'%(args.script, args.scriptparams)
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    print("Executing timeout monitor")
    toh = open("timeout.log","w")
    toh.write("Executing timeout monitor")
    timeouttime = starttime + timedelta(**{'seconds': int(args.timeout)})
    timoutcmd = '/opt/python/python36/bin/python36 ../htest/timeout.py --pid %s --ttime "%s"'%(res.pid, timeouttime)
    print("timeoutcmd is %s"%(timoutcmd))
    try:
        res_timeout = subprocess.Popen( timoutcmd, shell=True, stdout=toh, stderr=toh )
    except Exception as e:
        toh.write('Error Happened When Running timeout monitor with script:%s \nError:%s' % ( cmd, e ))
    toh.close()
    rtncode = res.wait()
    '''
    print("Collecting logs...")
    rtncode = ""
    try:
        testlog = ""
        mflag = 0
        oline = res.stdout.readline()
        while oline:
            print("while is working...")
            if len(testlog) <= 1024 * 1024:
                testlog += oline + "\n"
            else:
                if mflag == 0:
                    testlog += "\nMore log , please check testresult.log\n"
                    mflag = 1
            if psutil.pid_exists(int(res.pid)):
                print("pid exists, %s"%res.pid)
                oline = res.stdout.readline()
            else:
                break
            print("while is working, 1 loop over...")
        rtncode = res.wait()
        print("Log Collection Finished")
    except Exception as error:
        print("Something wrong happened when write log to file: %s"%error)
    '''
    
    print("return code is %s"%rtncode)
    testresult = ""
    if rtncode == rtnCode.SUCCEED:
        testresult = "SUCCEED"
    elif rtncode == rtnCode.TESTFAILED:
        testresult = "TESTFAILED"
    elif rtncode == rtnCode.SCRIPTFAILED:
        testresult = "SCRIPTFAILED"
    elif rtncode == rtnCode.ENVFAILED:
        testresult = "ENVFAILED"
    elif rtncode == rtnCode.TIMEOUT:
        testresult = "TIMEOUT"
    else:
        testresult = 'NA'

    print(testrunningdata)
    testrunningdata[args.testinstanceid]['log_path'] = args.testrundir + "/" + testinstance_dir
    testrunningdata[args.testinstanceid]['summary_html'] = args.testrundir + "/" + testinstance_dir + '/testresult_summary.html'
    testrunningdata[args.testinstanceid]['pid'] = res.pid
    
    #update the testrun data
    if rtncode == 0:
        testrunningdata['SUCCEED'] += 1
        testrunningdata['NOTRUN'] -= 1
    elif rtncode == 1:
        testrunningdata['TESTFAILED'] += 1
        testrunningdata['NOTRUN'] -= 1
    elif rtncode == 2:
        testrunningdata['SCRIPTFAILED'] += 1
        testrunningdata['NOTRUN'] -= 1
    elif rtncode == 3:
        testrunningdata['ENVFAILED'] += 1
        testrunningdata['NOTRUN'] -= 1
    #if not return by script, timeout happen at hight possiblity
    else:
        testrunningdata['TIMEOUT'] += 1
        testrunningdata['NOTRUN'] -= 1
        
    results = {
        "0":"SUCCEED",
        "-1":"TESTFAILED",
        "-2":"SCRIPTFAILED",
        "-3":"ENVFAILED",
        "-9":"TIMEOUT"
    }
    if rtncode not in ["-1","-2","-3","-9"]:
        testrunningdata[args.testinstanceid]['status'] = "NA"
    else:
        testrunningdata[args.testinstanceid]['status'] = results[rtncode]
    
    with open('/testdata/TEST_RUNNING_STAT/' + args.testruningstatfile, 'w') as fh:
        fh.write(json.dumps(testrunningdata))
    
    with open('/testdata/' + args.testrundir + "/testrun_summary.html", 'r+') as testrun_handle:
        testrundata = testrun_handle.read()
        '''
            <tr><td>tr_name</td><td><a href="tr_file_path">tr_file_path</a></td><td>tr_result</td></tr>
        '''
        testrundata = testrundata.replace('trstrs', '<tr><td>' + args.script + '</td><td><a href="./' + testinstance_dir + '">' + testinstance_dir + '</a></td><td>' + testresult + '</td></tr>trstrs')
        testrun_handle.seek(0)
        testrun_handle.write(testrundata)

    endtime = datetime.now()
    logfiles = os.listdir()
    testlog = ""

    for logfile in logfiles:
        '''
            <tr><td>tr_name</td><td><a href="tr_file_path">tr_file_path</a></td><td>tr_result</td></tr>
        '''
        testlog += '<tr><td>' + logfile + '</td><td><a href="./' + logfile + '">' + logfile + '</a></td></tr>'
    
    with open('/testdata/' + args.testrundir + '/' + testinstance_dir + "/testresult_summary.html", 'r+') as testresult_handle:
        testresultdata = testresult_handle.read()
        print("###############################################################################")
        print(testresultdata)
        print("###############################################################################")        
        testresultdata = testresultdata.replace('tctc', args.script)
        testresultdata = testresultdata.replace('titi', args.testinstanceid)
        testresultdata = testresultdata.replace('stst', str(starttime))
        testresultdata = testresultdata.replace('etet', str(endtime))
        testresultdata = testresultdata.replace('onon', args.owner)
        testresultdata = testresultdata.replace('rsrs', testresult)
        testresultdata = testresultdata.replace('tltl', testlog)
        testresult_handle.seek(0)
        testresult_handle.write(testresultdata)

if __name__ == '__main__':
    main()
