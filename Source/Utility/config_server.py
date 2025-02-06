import http.server
import socketserver

# Port to serve on
PORT = 400

# Directory where files are stored
DIRECTORY = "../../Data/Configs/"

class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files from the DIRECTORY folder."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        """Add CORS headers before finalizing the response headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept')
        super().end_headers()

# Start the server
with socketserver.TCPServer(("", PORT), CustomRequestHandler) as httpd:
    print(f"Serving files from {DIRECTORY} on port {PORT}")
    print(f"Access files at http://localhost:{PORT}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer is stopping...")
        httpd.server_close()