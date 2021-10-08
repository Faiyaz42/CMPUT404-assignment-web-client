#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Faiyaz Ahmed, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    #parsing the URL
    def get_URL_parts(self,url):
        PORT = 80
        PATH = "/"
        URL_parts = urllib.parse.urlparse(url) #parsing the URL components and dumping in a named tuple. We will extract hostname,port and path from this tuple. (https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse)
        hostname = URL_parts.hostname
        path = URL_parts.path
        port = URL_parts.port
        if port is None:                       #assign default port if port not given
            port = PORT
        if not path:                          #if the path is not given
            path = PATH
        return hostname, path, port

    #get the status code
    def get_code(self, data):
        return int(data.split()[1])

    #get the headers
    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    #get the body
    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        hostname, path, port = self.get_URL_parts(url)
        self.connect(hostname, port)   #establish socket connection using componeents from the parsed URL
        payload = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, hostname)        #create and send a payload as a request to the server
        self.sendall(payload)


        #response 
        response = self.recvall(self.socket)  
        
        #take response from the socket and get the header,code and body
        status_code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        print(status_code)
        print(headers)
        print(body)
        self.close()  #close connection
        

        return HTTPResponse(status_code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""


        hostname, path, port = self.get_URL_parts(url)
        self.connect(hostname, port)   #establish socket connection using componeents from the parsed URL

        content = "" 
        if args:
            content = urllib.parse.urlencode(args)  #take the args if passed to the fucntion and convert the str or byte object to a percent-encoded ASCII text string (https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode)
        cont_length = len(content)     #extract len of the ASCII string (if exists)
        cont_type = "application/x-www-form-urlencoded"       #content type
        payload = "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % (path, hostname, cont_type, cont_length)  #now create a payload with string contents
        # send request to the server
        self.sendall(payload + content)  #send payload and content (empty string if no content)

        #response 
        response = self.recvall(self.socket)  
        
        #take response from the socket and get the header,code and body
        status_code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        print(status_code)
        print(headers)
        print(body)
        self.close()  #close connection

        return HTTPResponse(status_code, body)
        

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
