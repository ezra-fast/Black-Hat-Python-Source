'''
This script uses WMI to monitor the local Windows system for process creation events. Upon a process being creation, details of the new child will be both
printed to the console and to an output file. This code provides the basis for more advanced monitoring tools that can be used both defensively and offensively.

One of the goals of process monitoring should be to identify processes that are launched by unprivileged users but have elevated privileges assigned to them.
These are the files that can be abused to elevate one's own privileges without assuming control of a privileged account itself.
'''

import os
import sys
import win32api
import win32con
import win32security
import wmi

def get_process_privileges(pid):
    try:
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)            # obtain a handle on the target process via OpenProcess()
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)                      # take a look at the process token
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)          # request the token information of the process based on the TokenPrivileges structure
        privileges = ''
        for priv_id, flags in privs:                            # privs is a list of tuples; the first index of each tuple is a privilege, the second index is whether or not it is enabled
            if flags == (win32security.SE_PRIVILEGE_ENABLED | win32security.SE_PRIVILEGE_ENABLED_BY_DEFAULT):       # we are only checking for the enabled bits (does the process have this privilege?)
                privileges += f'{win32security.LookupPrivilegeName(None, priv_id)}|'            # if the privilege is enabled, find the human readable name and add it to the string of privileges
    except Exception:
        privileges = 'N\A'
    
    return privileges

def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(f'{message}\r\n')

def monitor():
    head = 'CommandLine, Time, Executable, Parent PID, PID, User, Privileges'
    log_to_file(head)
    c = wmi.WMI()                                               # instantiate the WMI class
    process_watcher = c.Win32_Process.watch_for('creation')     # monitor the system for process creation events
    while True:
        try:
            new_process = process_watcher()                     # this loop blocks until a new process event is detected by process_watcher()
            cmdline = new_process.CommandLine                   # each process event is a WMI class called Win32_Process, which contains valuable child process info
            create_date = new_process.CreationDate
            executable = new_process.ExecutablePath
            parent_pid = new_process.ParentProcessId
            pid = new_process.ProcessId 
            proc_owner = new_process.GetOwner()                 # who spawned the process? 

            privileges = get_process_privileges(pid)            # privileges = 'N/A'
            process_log_message = (f'{cmdline} , {create_date} , {executable} , {parent_pid} , {pid} , {proc_owner} , {privileges}')
            print(process_log_message)          # print child process information to the console
            print()
            log_to_file(process_log_message)        # log child process information to a file
        except Exception:
            pass

if __name__ == "__main__":
    monitor()
