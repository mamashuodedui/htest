from datetime import datetime 
import argparse
import os, time, signal, sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Utility For Timeout Process Handling")
    parser.add_argument('-P','--pid', default='', required=True, help='PID of the executing testinstance ')
    parser.add_argument('-T','--ttime', default="1970-01-01 00:00:00", required=False, help='expired time value for testing')
    args = parser.parse_args()

    ctime = str(datetime.now())
    while ctime < args.ttime:
        time.sleep(5)
        ctime = str(datetime.now())
    cmd = 'ps -ef|grep %s|grep -v grep|awk \'{print $2}\'' % (args.pid)
    res = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pids = res.stdout.read().rstrip().split("\n")
    for pid in pids:
        try:
            os.kill(int(pid), signal.SIGKILL)
            print("Timeout Time Reached, Killing PID: %s"%(pid))
        except OSError:
            print("No Such PID Exists")
        except Exception as error:
            print("Error Happened When Kill PID: %s: %s"%( pid, error ))

if __name__ == '__main__':
    sys.exit(main())