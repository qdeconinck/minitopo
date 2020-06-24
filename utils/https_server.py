'''
From :
http://code.activestate.com/recipes/442473-simple-http-server-supporting-ssl-secure-communica/

SimpleSecureHTTPServer.py - simple HTTP server supporting SSL.

- replace fpem with the location of your .pem server file.
- the default port is 443.

usage: python SimpleSecureHTTPServer.py
'''

import sys
if sys.version_info[0] == 3:
    # Python 3
    import http.server, ssl
    server_address = ('', 443)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                server_side=True,
                                certfile=sys.argv[1],
                                ssl_version=ssl.PROTOCOL_TLS)
    print("Serving HTTPS on 0.0.0.0 port 443...")
    httpd.serve_forever()
else:
    # Python2
    import BaseHTTPServer, SimpleHTTPServer
    import ssl
    import os

    httpd = BaseHTTPServer.HTTPServer(('', 443), SimpleHTTPServer.SimpleHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=sys.argv[1], server_side=True)

    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])

    print("Serving HTTPS on 0.0.0.0 port 443...")
    httpd.serve_forever()