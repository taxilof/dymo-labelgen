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
import os.path



def call_printer (text, font_size, font_type, action):

    if ('print' in action):
        cmd = './main.py "' + text + '" --size=small --noconfirm --print --font ' + font_type + ' --font_size='+font_size
    else:
        cmd = './main.py "' + text + '" --size=small --noconfirm --font ' + font_type + ' --font_size='+font_size
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
            file_data = f.read().replace('RANDOM',str(time.time())).replace('TEXT_VALUE',self.last_text_value)
            file_data = file_data.replace('FONT_SIZE', self.last_text_size).replace('FONT_TYPE', self.last_text_font)
            self.wfile.write(str.encode(file_data))
            
    def do_GET(self):
        label_png_path = "label.png"
        if label_png_path in self.path and os.path.isfile(label_png_path) :
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
        call_printer(params['text'], params['size'], params['font'], params['action'])
        self.last_text_value = urllib.parse.unquote(params['text']).replace('+',' ')
        self.last_text_font = params['font']
        self.last_text_size = params['size']
        
        self.send_index()
        return

ConfigHTTPRequestHandler.protocol_version = "HTTP/1.0"
ConfigHTTPRequestHandler.last_text_value = ""
ConfigHTTPRequestHandler.last_text_font = "Helvetica"
ConfigHTTPRequestHandler.last_text_size = "20"
httpd = HTTPServer(("0.0.0.0", 5555), ConfigHTTPRequestHandler)

sa = httpd.socket.getsockname()
print("Serving HTTP on", sa[0], "port", sa[1], "...")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received, exiting.")
    httpd.server_close()
    sys.exit(0)