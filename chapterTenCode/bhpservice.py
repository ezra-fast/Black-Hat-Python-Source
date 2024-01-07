'''
This is an intentionally vulnerable service that periodically copies a script to a temporary file location and runs that script with it's own privileges.
This can be exploited by an attacker who injects malicious code into the script being executed because the integrity of the file is not verified before it is executed.
This is an extremely common vulnerability that will always exist. It is the result of sloppy programming.
'''

'''
Creating executable: pyinstaller -F --hiddenimport win32timezone bhservice.py

Downloading the vbs script dependency: https://nostarch.com/black-hat-python2E/

Service commands (require administrative privileges): bhservice.exe install | start | stop | update | remove
'''

import os
import servicemanager
import shutil
import subprocess
import sys

import win32event
import win32service
import win32serviceutil

SRCDIR = 'C:\\Users\\super\\work'
TGTDIR = 'C:\\Windows\\TEMP'

class BHServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "BlackHatService"
    _svc_display_name_ = 'Black Hat Service'
    _svc_description_ = ("Executes VBScripts at regular intervals." + " What could possibly go wrong?")

    def __init__(self, args):
        self.vbs = os.path.join(TGTDIR, 'bhservice_task.vbs')               # where the vbs script will go to execute
        self.timeout = 1000 * 60                                            # setting a timeout of 1 minute

        win32serviceutil.ServiceFramework.__init__(self, args)              # initialize the Service Framework
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)           # Create the event object

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)         # set the service status
        win32event.SetEvent(self.hWaitStop)                                 # stop the service

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)              # start the service
        self.main()                                                         # call the main function of the service

    def main(self):
        while True:                                                                     # this loop only runs every minute because of self.timeout
            ret_code = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if ret_code == win32event.WAIT_OBJECT_0:                                    # if the service receives the stop signal, break out of this loop
                servicemanager.LogInfoMsg("Service is stopping")
                break
            src = os.path.join(SRCDIR, 'bhservice_task.vbs')
            shutil.copy(src, self.vbs)                                              # copy the script to the target directory
            subprocess.call(f"cscript.exe {self.vbs}", shell=False)                 # execute the script in the target directory
            os.unlink(self.vbs)                                                     # remove the script from the temporary location

if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BHServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BHServerSvc)

