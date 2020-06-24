'''
From :
http://code.activestate.com/recipes/442473-simple-http-server-supporting-ssl-secure-communica/

SimpleHTTPServer.py - simple HTTP server supporting SSL.

- the default port is 80.

usage: python SimpleHTTPServer.py
'''

import socket, os
try:
    # Python 2
    from SocketServer import BaseServer
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except ImportError:
    # Python 3
    from socketserver import BaseServer
    from http.server import HTTPServer, SimpleHTTPRequestHandler

from OpenSSL import SSL

def test(HandlerClass=SimpleHTTPRequestHandler,
         ServerClass=HTTPServer):
    server_address = ('', 80)  # (address, port)
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")
    httpd.serve_forever()


if __name__ == '__main__':
    test()
