'''
This script takes in a capture file, finds all TCP conversations, sifts through each conversation for packets (responses) that contain images, 
creates a single buffer with all packet payloads (all image content) for the conversation, and writes the resultant images to disk.

Change the hardcoded file paths as needed
'''

'''
Dependencies:
    - wget http://eclecti.cc/files/2008/03/haarcascade_frontalface_alt.xml
    - apt install libopencv-dev python3-opencv python3-numpy python3-scipy
'''

from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib

OUTDIR = '/home/ezra/blackHatPython/chapterFourCode/test'       # output location of images
PCAPS = '/home/ezra/blackHatPython/chapterFourCode/test'        # output location of pcap captures

Response = collections.namedtuple('Response', ['header', 'payload'])        # easier that creating a Response class to instantiate responses

def get_header(payload):        # take in raw HTTP and return the headers
    try:
        header_raw = payload[:payload.index(b'\r\n\r\n')+2]     # the header starts at the beginning of the packet and ends with newlines and carriage returns
    except ValueError:                  # if there's an error extracting the payload, write '-' to the console and return None
        sys.stdout.write('-')
        sys.stdout.flush()
        return None

    header = dict(re.findall(r'(?P<name>.*?) : (?P<value>/*?)\r\n', header_raw.decode()))       # making a dictionary out of the decoded payload
    if 'Content-Type' not in header:
        return None                     # if not the content looking for, return None
    return header

# Response is a namedtuple with two attributes --> the header and the payload

def extract_content(Response, content_name='image'):        # extracting the content from the response (takes in the Response and the type of content to extract)
    content, content_type = None, None
    if content_name in Response.header['Content-Type']:     # all responses with images in them will have 'image' in the Content-Type attribute
        content_type = Response.header['Content-Type'].split('/')[1]        # take the actual image file format
        content = Response.payload[Response.payload.index(b'\r\n\r\n')+4:]      # everything in the payload after the header

        if 'Content-Encoding' in Response.header:               # if the content has been encoded, decompress using the zlib module
            if Response.header['Content-Encoding'] == "gzip":
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header['Content-Encoding'] == "deflate":
                content = zlib.decompress(Response.payload)

    return content, content_type        # returning the payload (content after the header), and the type of image

class Recapper:
    def __init__(self, fname):          # initializing the new object with the name of the pcap we want to read
        pcap = rdpcap(fname)
        self.sessions = pcap.sessions()     # automatically separate each TCP session into a dict that contains each complete TCP stream
        self.responses = list()             # list that will be filled with the responses from the capture

    def get_responses(self):                # traverse the packets to find each Response, add each one to the list of responses present in the packet stream
        for session in self.sessions:       # iterate through the dictionary of complete TCP sessions
            payload = b''
            for packet in self.sessions[session]:       # now iterate through each packet (in each session)
                try:
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:      # we only want traffic that is to or from port 80
                        payload += bytes(packet[TCP].payload)                   # concatenating all payloads together into a single buffer to reconstruct transmitted material (images)
                except IndexError:                                          # if no TCP payload in the packet, print 'x' to the console and keep going
                    sys.stdout.write('x')
                    sys.stdout.flush()
                
            if payload:                         # if the payload is not empty after concatenating all payloads together
                header = get_header(payload)    # extract the header
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))     # append the Response to the responses list

    def write(self, content_name):      # writing images found in the capture to the specified output directory
        # go through the list of responses and if it contains an image, write the image to disk
        for i, response in enumerate(self.responses):                                               # iterate through responses
            content, content_type = extract_content(response, content_name)                         # extract the content
            if content and content_type:
                fname = os.path.join(OUTDIR, f'ex_{i}.{content_type}')                              # creating the path
                print(f"Writing {fname}")
                with open(fname, 'wb') as f:                                                        # writing the image to it's own file
                    f.write(content)

if __name__ == '__main__':
    pfile = os.path.join(PCAPS, 'pcap.pcap')                # this is the capture file to operate on 
    recapper = Recapper(pfile)                              # create a Recapper object
    recapper.get_responses()                                # finding all the responses from the pcap file
    recapper.write('image')                                 # write the extracted images from the responses to disk
