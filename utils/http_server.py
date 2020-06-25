'''
From :
http://code.activestate.com/recipes/442473-simple-http-server-supporting-ssl-secure-communica/

SimpleHTTPServer.py - simple HTTP server supporting SSL.

- the default port is 80.

usage: python SimpleHTTPServer.py
'''

import sys
if sys.version_info[0] == 3:
    # Python 3
    import http.server
    server_address = ('', 80)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    print("Serving HTTP on 0.0.0.0 port 80...")
    httpd.serve_forever()
else:
    # Python2
    import BaseHTTPServer, SimpleHTTPServer
    import os

    httpd = BaseHTTPServer.HTTPServer(('', 443), SimpleHTTPServer.SimpleHTTPRequestHandler)
    print("Serving HTTP on 0.0.0.0 port 80...")
    httpd.serve_forever()