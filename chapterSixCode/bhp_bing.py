'''
This script will not work as shown in the book due to the fact that Microsoft now charges for the use of Bing API keys (even at the "free" tier)
If you are willing to pay the resource is: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/create-bing-search-service-resource
'''

'''
When working as intended with a proper, valid API key this script will take the IP address and/or hostname of the server a web application is running on
and add the other web applications running on the same server to the Target Scope; It will also enumerate the subdomains of the web application being analyzed.

This is accomplished through the use of Bing Search API and the use of the IP and Domain search modifiers, which used to be available for free.
'''

'''
Instructions:
	- Add this script as an extension in Burp Suite
	- Populate the Site Map
	- Right click the request
	- Extensions > BHP Bing > Send to Bing
	- Go to Extensions > Output
'''

from burp import IBurpExtender
from burp import IContextMenuFactory

from java.net import URL
from java.util import ArrayList
from javax.swing import JMenuItem
from thread import start_new_thread

import json
import socket
import urllib
API_KEY = '{API_KEY}'
API_HOST = 'api.cognitive.microsoft.com'

class BurpExtender(IBurpExtender, IContextMenuFactory):     # Providing a Context Menu when a user right-clicks a request in Burp
    def registerExtenderCallbacks(self, callbacks):         # This menu will display a "Send to Bing" selection as defined below
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self.context    = None

        # we set up our extension
        callbacks.setExtensionName("BHP Bing")
        callbacks.registerContextMenuFactory(self)  # Registering a Menu Handler to determine which site the user clicked so we can construct our queries
                                                        
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))    # render the menu item and handle the click event with bing_menu()
        return menu_list

    def bing_menu(self, event):                                 # this function is called when the user clicks the context menu item defined above

        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()       # retrieving the highlighted HTTP request(s)

        print('%d requests highlighted' % len(http_traffic))

        for traffic in http_traffic:
            http_service    = traffic.getHttpService()
            host            = http_service.getHost()            # retrieving the host portion of the request

            print("User selected host: %s" % host)
            self.bing_search(host)                              # sending it for further processing

        return

    def bing_search(self, host):
        # check if we have an IP or a hostname
        try:
            is_ip = bool(socket.inet_aton(host))                # True if IP address, False otherwise
        except socket.error:
            is_ip = False

        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)             # if we have hostname, find IP address thereof
            domain = True

        start_new_thread(self.bing_query, ('ip:%s' % ip_address,))     # querying Bing for all virtual hosts that have the same IP address

        if domain:
            start_new_thread(self.bing_query, ('domain:%s' % host,))   # perform a second search for all subdomains of the domain being processed

	'''
	Burp Suite's HTTP API requires that the entire HTTP request is built as a string before sending it.
	'''

    def bing_query(self, bing_query_string):
        print('Performing Bing Search: %s' % bing_query_string)
        http_request = 'GET https://%s/bing/v7.0/search?' % API_HOST
        # encode our query
        http_request += 'q=%s HTTP/1.1\r\n' % urllib.quote(bing_query_string)
        http_request += 'Host: %s\r\n' % API_HOST
        http_request += 'Connection:close\r\n'
        http_request += 'Ocp-Apim-Subscription-Key: %s\r\n' % API_KEY
        http_request += 'User-Agent: Black Hat Python\r\n\r\n'			# manually creating the string

        json_body = self._callbacks.makeHttpRequest(API_HOST, 443, True, http_request).tostring()	# making the API call
        json_body = json_body.split('\r\n\r\n', 1)[1]							# splitting off the headers

        try:
            response = json.loads(json_body)					# passing the JSON body to the JSON parser
        except (TypeError, ValueError) as err:
            print('No results from Bing: %s' % err)
        else:							# this conditional block executes if the JSON body can be parsed; it displays information about the discovered site
            sites = list()
            if response.get('webPages'):
                sites = response['webPages']['value']
            if len(sites):
                for site in sites:
                    print('*'*100)
                    print("Name: %s" % site['name'])
                    print("URL: %s" % site['url'])
                    print("Description: %r" % site['snippet'])
                    print('*'*100)

                    java_url = URL(site['url'])
                    if not self._callbacks.isInScope(java_url):		# if not already in Burp Suite target scope
                        print("Adding %s to Burp Scope" %  site['url'])
                        self._callbacks.includeInScope(java_url)	# add to Burp Suite target scope
                    else:
                        print('Empty response from Bing.: %s' % bing_query_string)
        return


