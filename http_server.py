#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import socket
import sys
import subprocess as proc
import json
import time
import urllib.parse



def call_printer (text, font_size, action):

    if ('print' in action):
        cmd = './main.py "' + text + '" --size=small --noconfirm --print --font_size='+font_size
    else:
        cmd = './main.py "' + text + '" --size=small --noconfirm --font_size='+font_size
    print(cmd)
    proc.check_call(cmd,shell=True)
    
    
class ConfigHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, mimetype):
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()

    def send_index(self):
        self._set_headers('text/html')
        file_path = "index.html"
        with open(file_path, "r") as f:
            file_data = f.read().replace("RANDOM",str(time.time())).replace("TEXT_VALUE",self.last_text_value)
            self.wfile.write(str.encode(file_data))
            
    def do_GET(self):
        if "label.png" in self.path:
            self._set_headers('image/png')
            file_path = "label.png"
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_index()

    def do_HEAD(self):
        self._set_headers('text/html')

    def do_POST(self):
        #print(self.headers)

        content_length = int(self.headers.get('Content-Length', 0))
        config_string = self.rfile.read(content_length).decode("UTF-8")
        print("Content length: ", content_length)
        print("Config string: [ ", config_string, " ]")
        
        # extract params and call printer script
        params = dict(x.split('=') for x in config_string.split('&'))
        print("params: " + str(params))
        call_printer(params['text'], params['size'], params['action'])
        self.last_text_value = urllib.parse.unquote(params['text']).replace('+',' ')

        self.send_index()
        return

ConfigHTTPRequestHandler.protocol_version = "HTTP/1.0"
ConfigHTTPRequestHandler.last_text_value = ""
httpd = HTTPServer(("0.0.0.0", 5555), ConfigHTTPRequestHandler)

sa = httpd.socket.getsockname()
print("Serving HTTP on", sa[0], "port", sa[1], "...")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received, exiting.")
    httpd.server_close()
    sys.exit(0)