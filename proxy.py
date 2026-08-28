import http.server
import socketserver
import json

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        print(f"Headers:\n{self.headers}")
        content_length_str = self.headers.get('Content-Length')
        if content_length_str:
            content_length = int(content_length_str)
            post_data = self.rfile.read(content_length)
            print(f"Body: {post_data.decode('utf-8')}")
        else:
            print("No Content-Length header. Trying to read chunked or empty...")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"prediction":"STAY","probability":0.1,"risk_level":"LOW","model_version":"test","decision_threshold":0.5}')

with socketserver.TCPServer(("", 8003), Handler) as httpd:
    print("Serving at port 8003")
    httpd.serve_forever()

