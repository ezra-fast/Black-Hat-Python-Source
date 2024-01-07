'''
This is a multipurpose SSH2 client that can execute single commands on remote machines
'''

import paramiko

# paramiko supports both password and key based authentication

'''
ssh_command():
    - make connection to SSH server and run a single command
    - 
'''

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    # setting policy to accept the key for the server we're connecting to.
    client.connect(ip, port=port, username=user, password=passwd)   # making the connection

    _, stdout, stderr = client.exec_command(cmd)    # executing the command assuming the connection has been made
    output = stdout.readlines() + stderr.readlines()
    if output:      # if the command produces output, print each line
        print('--- Start Output ---')
        for line in output:
            print(line.strip())
        print('--- End Output ---')

if __name__ == '__main__':
    import getpass
    # user = getpass.getuser()
    user = input('Username: ')      # collecting credentials
    password = getpass.getpass()

    ip = input('Enter server IP: ') # or '192.168.0.X'
    port = input('Enter port or <CR>: ') or 22
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)      # using the gathered input to execute a command on the remote machine
