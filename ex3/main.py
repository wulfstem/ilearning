from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from math import gcd
import os

PORT = int(os.getenv("PORT", 8080))

class MyRequestHandler(BaseHTTPRequestHandler):

    def lcm(self, x, y):
        return x * y // gcd(x, y)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/vilkaitis_ervinas_gmail_com":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"NaN")
            return

        params = parse_qs(parsed_url.query)
        x = params.get("x", [None])[0]
        y = params.get("y", [None])[0]

        if x is None or y is None or not x.isdigit() or not y.isdigit():
            self.send_plain("NaN")
            return
        
        x = int(x)
        y = int(y)
        result = str(self.lcm(x, y))
        self.send_plain(result)

    def send_plain(self, text):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(text.encode())

def main():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print('Starting server...')
    httpd.serve_forever()

if __name__ == '__main__':
    main()