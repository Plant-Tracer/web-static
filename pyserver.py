'''
pyserver - a simple HTTP server for running planttracer.com locally
    Credit: https://stackoverflow.com/questions/56825520/using-python-simplehttpserver-to-serve-files-without-html, Emrah Diril, user:30581

    This will serve the files in the current working directory and crucially
    for planttracer.com will interpret files without an extension as .html

    Usage:
    cd <my-web-server-files-root>
    python3 .../pyserver.py
'''

import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

PORT = 9000

Handler = http.server.SimpleHTTPRequestHandler

Handler.extensions_map={
    '.html': 'text/html',
    '': 'text/html', # Default is 'application/octet-stream'
    }

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()

