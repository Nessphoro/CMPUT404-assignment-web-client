#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
from collections import defaultdict
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
        self.socket = socket.create_connection((host, port))
        return None
    
    def close(self):
        self.socket.close()
    
    def setup(self, url):
        u = urllib.parse.urlparse(url)
        assert u.hostname is not None
        host = u.hostname
        port = u.port if u.port is not None else 80
        self.host = u.netloc
        self.port = port
        self.path = u.path if u.path else "/"
        self.connect(host, port)

    def parse_status(self):
        self.ver, self.code, self.text = self.data[0].split(" ", maxsplit=2)
        self.code = int(self.code)
        # print(self.data)
    
    def parse_headers(self):
        self.headers = defaultdict(list)
        for i in range(1, len(self.data)):
            if self.data[i] == '\r':
                self.endh = i + 1
                break
            h, v = self.data[i].split(":", maxsplit=1)
            self.headers[h].append(v)



    def write_header(self, header):
        # print(f"> {header[0]}: {header[1]}")
        self.socket.sendall(f"{header[0]}: {header[1]}\r\n".encode("utf-8"))
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
        self.setup(url)
        self.socket.sendall(f"GET {self.path} HTTP/1.1\r\n".encode("utf-8"))
        self.write_header(("Host", self.host))
        self.write_header(('Accept-Encoding', "identity"))
        self.write_header(('Accept-Charset', "utf-8"))
        self.write_header(("User-Agent", "curl/7.54.0"))
        self.write_header(("Accept", "*/*"))
        self.write_header(("Connection", "close"))
        self.socket.sendall(b"\r\n")
        self.socket.shutdown(socket.SHUT_WR)
        
        self.data = self.recvall(self.socket).split("\n")
        self.parse_status()
        self.parse_headers()
        self.close()
        return HTTPResponse(self.code, '\n'.join(self.data[self.endh:]))


    def POST(self, url, args=dict()):
        senddata = urllib.parse.urlencode(args).encode("utf-8")

        self.setup(url)
        self.socket.sendall(f"POST {self.path} HTTP/1.1\r\n".encode("utf-8"))
        self.write_header(("Host", self.host))
        self.write_header(("Content-Type", "application/x-www-form-urlencoded"))
        self.write_header(("Content-Length", str(len(senddata))))
        self.write_header(('Accept-Encoding', "identity"))
        self.write_header(('Accept-Charset', "utf-8"))
        self.write_header(("User-Agent", "curl/7.54.0"))
        self.write_header(("Accept", "*/*"))
        self.write_header(("Connection", "close"))
        self.socket.sendall(b"\r\n")
        self.socket.sendall(senddata)
        self.socket.shutdown(socket.SHUT_WR)
        
        self.data = self.recvall(self.socket).split("\n")
        self.parse_status()
        self.parse_headers()
        self.close()
        return HTTPResponse(self.code, '\n'.join(self.data[self.endh:]))
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
