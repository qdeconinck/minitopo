'''
From :
http://code.activestate.com/recipes/442473-simple-http-server-supporting-ssl-secure-communica/

SimpleHTTPServer.py - simple HTTP server supporting SSL.

- the default port is 80.

usage: python SimpleHTTPServer.py
'''

import socket, os
from SocketServer import BaseServer
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from OpenSSL import SSL


def test(HandlerClass=SimpleHTTPRequestHandler,
         ServerClass=HTTPServer):
    server_address = ('', 80)  # (address, port)
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print("Serving HTTPS on", sa[0], "port", sa[1], "...")
    httpd.serve_forever()


if __name__ == '__main__':
    test()
