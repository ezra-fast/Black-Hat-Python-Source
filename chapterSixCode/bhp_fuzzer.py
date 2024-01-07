'''
This script is a simple python implementation of a Burp Intruder extension that can be used to fuzz the target application;
The fuzzing operations defined herein are relatively simple and should be rendered more sophisticated for production;
The effectiveness of fuzzing is also largely dependent on the parts of the request being fuzzed with payloads;
'''

'''
Using this script within Burp Suite:
	- Make sure Burp is configured to point at Jython as the python environment
	- Load this script as a Burp Extension (both standard output and standard error in the UI)
	- Proxy > Intercept --> intercept an HTTP POST request to the target server with arbitary parameters
	- Once this request is in the intercept window, right click and send to the Intruder
	- Intruder > Positions > Auto --> make sure that query parameter fields are highlighted within payload delimeters; this marks them for fuzzing
	- Payload Options > Select Generator > BHP Payload Generator
	- Intruder > Start Attack
'''

from burp import IBurpExtender				# Importing the classes we need from burp (this is required for every burp extension)
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator

from java.util import List, ArrayList

import random

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):		# this class extends the IBurpExtender and IIntruderPayloadGeneratorFactory classes
	def registerExtenderCallbacks(self, callbacks):
		self._callbacks = callbacks
		self._helpers	= callbacks.getHelpers()
		
		callbacks.registerIntruderPayloadGeneratorFactory(self)		# registering our class so that the Intruder tool is aware that we can generate payloads
		
		return
		
	def getGeneratorName(self):						# Providing a name to the newly defined payload generator
		return "BHP Payload Generator"
		
	def createNewInstance(self, attack):				# Receive the 'attack' parameter and return an instance of the IIntruderPayloadGenerator
		return BHPFuzzer(self, attack)
		
class BHPFuzzer(IIntruderPayloadGenerator):             # This class extends the IIntruderPayloadGenerator class
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self.attack = attack
        self.max_payloads = 50                          # max_payloads and num_iterations are the limiters of the fuzzing; increase as necessary
        self.num_iterations = 0

        return

    def hasMorePayloads(self):                          # Checking if we've reached the end of the payloads
        if self.num_iterations == self.max_payloads:
            return False
        else:
            return True

    def getNextPayload(self, current_payload):           # Receives the original HTTP payload (byte array), this is what is getting fuzzed
        # convert into a string
        payload = "".join(chr(x) for x in current_payload)      # convert the byte array (payload) into a string

        # call our simple mutator to fuzz the POST
        payload = self.mutate_payload(payload)                  # mutate the payload itself

        # increase the number of fuzzing attempts
        self.num_iterations += 1

        return payload                                          # return the mutated payload

    def reset(self):                                            # reset the number of iterations
        self.num_iterations = 0
        return

    def mutate_payload(self, original_payload):                     # performing the modification of the request body
        # pick a simple mutator or even call an external script
        picker = random.randint(1, 3)

        # select a random offset in the payload to mutate
        offset = random.randint(0, len(original_payload) - 1)

        front, back = original_payload[:offset], original_payload[offset:]      # splitting the payload into two random length chunks

        # random offset insert an SQL Injection attempt     --> single quote at the end of the front chunk
        if picker == 1:
            front += "'"
        
        # throw an XSS attempt in                           --> script tag to the end of the front chunk
        elif picker == 2:
            front += "<script>alert('Busted');</script>"

        # repeat a random chunk of the original payload
        elif picker == 3:
            chunk_length = random.randint(0, len(back) - 1)     # random offset from the front chunk
            repeater = random.randint(1, 10)                    # a random number of times to repeat the chunk
            for _ in range(repeater):
                front += original_payload[:offset + chunk_length] # add the random front sub-chunk to the end of the front chunk 'repeater' number of times

        return front + back                                     # returning the mutated front chunk with the back chunk appended



