import json
import os
from datetime import datetime, timedelta
import argparse
import subprocess
import shutil
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
    parser.add_argument('-F','--testrunningstatfile', default='',required=True, help='testrunning stat file')
    parser.add_argument('-O','--owner', default='admin',required=True, help='test owner')
    parser.add_argument('-T','--topo', default=1,required=True, help='topology: 1.single, 2.b2b 3.multiple')

    args = parser.parse_args()
    
    #parsing suts
    suts_raw = json.loads(args.suts)
    print(type(suts_raw))
    print(suts_raw)
    suts = []
    params = " "
    scriptparams = json.loads(args.scriptparams)
    #["Server_Lenovo|1.1.1.1|root1|password|sn:11111111", "Server_Huawei|2.2.2.2|root1|password|sn:22222222"]
    if 'iplist' in args.scriptparams:
        for sut in suts_raw:
            with open('iplist','w') as ipf:
                ipf.write(sut.split('|')[1]+"\n")
        for param in args.scriptparams:
            params += param['value'] + " "
            
    elif 'ippluslist' in args.scriptparams:
        for sut in suts_raw:
            with open('ippluslist','w') as ippf:
                ippf.write(sut.split('|')[1] + "|" + sut.split('|')[2] + "|" + sut.split('|')[3] + "\n")
        for param_key in scriptparams.keys():
            params += scriptparams[param_key] + " "
    
    elif 'suts' in args.scriptparams:
        if int(args.topo) == 1 or int(args.topo) == 3:
            sut = suts_raw[0].split("|")
            suts.append({"addr":sut[1], "username":sut[2], "password":sut[2]})
        elif int(args.topo) == 2:
            for sut in suts_raw:
                s = sut.split("|")
                suts.append({"addr":s[1], "username":s[2], "password":s[3]})
        else:
            print("#RUNTASK: already hanlded at runjob")        
        for param_key in scriptparams.keys():
            if 'suts' in param_key:
                continue
            else:
                params += scriptparams[param_key] + " "
    else:
        print("#RUNTASK: NO SUT found to execute")
        return rtnCode.SCRIPTFAILED
    
    print("#RUNTASK: Check Test Environment")
    if not os.path.ismount('/testdata'):
        return rtnCode.ENVFAILED
    
    print("#RUNTASK: Create testresult directory")
    t = datetime.now()
    starttime = t
    testinstance_dir = "_".join([os.path.basename(args.script).split('.')[0], str(t.year), str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second), str(t.microsecond)])
    os.mkdir(testinstance_dir)
    os.chdir(testinstance_dir)

    print("#RUNTASK: move Template File to testresult directory")
    shutil.copyfile('../htest/templates/testresult_summary.html','testresult_summary.html')

    print("#RUNTASK: Parsing testing data")
    with open('/testdata/TEST_RUNNING_STAT/' + args.testrunningstatfile, 'r') as testrunning_handle:
        temp_data = testrunning_handle.read()
        testrunningdata = json.loads(temp_data)

    if str(args.interpreter).lower() == 'shell':
        if 'iplist' in args.scriptparams:
            cmd = 'source ../htest/venv/bin/activate && sh ../%s %s '%(args.script, "iplist", params)
        elif 'ippluslist' in args.scriptparams:
            cmd = 'source ../htest/venv/bin/activate && sh ../%s %s '%(args.script, "ippluslist", params)
        else:
            cmd = 'source ../htest/venv/bin/activate && sh ../%s %s '%(args.script, params)
    elif str(args.interpreter).lower() == 'python':
        cmd = 'source ../htest/venv/bin/activate && /opt/python/python36/bin/python36 ../%s %s --suts %s'%(args.script, params, json.dumps(suts))
        
    print("#RUNTASK: Executing script: %s" % cmd)                                             
        
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    
    #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
    testrunningdata['testinstances'][args.testinstanceid]['status_id'] = 4
    testrunningdata['testinstances'][args.testinstanceid]['testrun_id'] = args.testrunid
    testrunningdata['testinstances'][args.testinstanceid]['log_path'] = args.testrundir + "/" + testinstance_dir
    testrunningdata['testinstances'][args.testinstanceid]['summary_html'] = args.testrundir + "/" + testinstance_dir + '/testresult_summary.html'
    testrunningdata['testinstances'][args.testinstanceid]['pid'] = res.pid
    with open('/testdata/TEST_RUNNING_STAT/' + args.testrunningstatfile, 'w') as fh:
        fh.write(json.dumps(testrunningdata))

    print("#RUNTASK: Executing timeout monitor")
    timeouttime = starttime + timedelta(**{'seconds': int(args.timeout)})
    timoutcmd = '/opt/python/python36/bin/python36 ../htest/timeout.py --pid %s --ttime "%s"'%(res.pid, timeouttime)
    print("#RUNTASK: timeoutcmd is %s"%(timoutcmd))
    try:
        res_timeout = subprocess.Popen( timoutcmd, shell=True )
    except Exception as e:
        print('#RUNTASK: Error Happened When Running timeout monitor with script:%s \nError:%s' % ( cmd, e ))
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
    
    print("#RUNTASK: testrunning data as below:")
    print(testrunningdata)    
    #update the testrun data
    testresult = ""
    print("#RUNTASK: rtncode type is %s, value is %s"%(type(rtncode), rtncode))
    if int(rtncode) == rtnCode.SUCCEED:
        testresult = "SUCCEED"
        testrunningdata['SUCCEED'] += 1
        if testrunningdata['NOTRUN'] != 0:
            testrunningdata['NOTRUN'] -= 1
        #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
        testrunningdata['testinstances'][args.testinstanceid]['status_id'] = 0
    elif int(rtncode) == rtnCode.TESTFAILED:
        testresult = "TESTFAILED"
        testrunningdata['TESTFAILED'] += 1
        if testrunningdata['NOTRUN'] != 0:
            testrunningdata['NOTRUN'] -= 1
        #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
        testrunningdata['testinstances'][args.testinstanceid]['status_id'] = -1
    elif int(rtncode) == rtnCode.SCRIPTFAILED:
        testresult = "SCRIPTFAILED"
        testrunningdata['SCRIPTFAILED'] += 1
        if testrunningdata['NOTRUN'] != 0:
            testrunningdata['NOTRUN'] -= 1
        #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
        testrunningdata['testinstances'][args.testinstanceid]['status_id'] = -2
    elif int(rtncode) == rtnCode.ENVFAILED:
        testresult = "ENVFAILED"
        testrunningdata['ENVFAILED'] += 1
        if testrunningdata['NOTRUN'] != 0:
            testrunningdata['NOTRUN'] -= 1
        #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
        testrunningdata['testinstances'][args.testinstanceid]['status_id'] = -3
    elif int(rtncode) == rtnCode.TIMEOUT:
        testresult = "TIMEOUT"
        testrunningdata['TIMEOUT'] += 1
        if testrunningdata['NOTRUN'] != 0:
            testrunningdata['NOTRUN'] -= 1
        #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
        testrunningdata['testinstances'][args.testinstanceid]['status_id'] = -9
    #if not return by script, timeout happen at hight possiblity
    else:
        testresult = 'NA'
        testrunningdata['NA'] += 1
        if testrunningdata['NOTRUN'] != 0:
            testrunningdata['NOTRUN'] -= 1
        #0.SUCCEED -1.TESTFAILED -2.SCRIPTFAILED -3.ENVFAILED -9.TIMEOUT 4.NA 5.NOTRUN
        testrunningdata['testinstances'][args.testinstanceid]['status_id'] = 4

    results = {
        "0":"SUCCEED",
        "-1":"TESTFAILED",
        "-2":"SCRIPTFAILED",
        "-3":"ENVFAILED",
        "-9":"TIMEOUT",
        "4":"NA",
        "5":"NOTRUN"
    }
    if str(rtncode) in results.keys():
        testrunningdata['testinstances'][args.testinstanceid]['status'] = results[str(rtncode)]
    else:
        testrunningdata['testinstances'][args.testinstanceid]['status'] = "NA"
    
    print("#RUNTASK: update testrun statistics")
    with open('/testdata/TEST_RUNNING_STAT/' + args.testrunningstatfile, 'w') as fh:
        fh.write(json.dumps(testrunningdata))

    print("#RUNTASK: update testrun summary")
    with open('/testdata/' + args.testrundir + "/testrun_summary.html", 'r+') as testrun_handle:
        testrundata = testrun_handle.read()
        '''
            <tr><td>tr_name</td><td><a href="tr_file_path">tr_file_path</a></td><td>tr_result</td></tr>
        '''
        testrundata = testrundata.replace('trstrs', '<tr><td>' + args.script + '</td><td><a href="./' + testinstance_dir + '/testresult_summary.html">testresult_summary</a></td><td>' + testresult + '</td></tr>trstrs')
        testrun_handle.seek(0)
        testrun_handle.write(testrundata)

    print("#RUNTASK: update testresult summary")
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
