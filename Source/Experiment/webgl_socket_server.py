import http.server
import socketserver
import os
import webbrowser
import asyncio
import threading
import sys
import logging
from http.server import SimpleHTTPRequestHandler, HTTPServer


class GzipRequestHandler(SimpleHTTPRequestHandler):
    '''HTTPRequestHandler for gzip files'''

    def end_headers(self):
        '''Set Content-Encoding: gzip for gzipped files'''
        if self.path.endswith('.gz'):
            self.send_header('Content-Encoding', 'gzip')
        super().end_headers()

    def do_GET(self):
        '''Set Content-Encoding and Content-Type to gzipped files'''
        path = self.translate_path(self.path)
        if path.endswith('.js.gz'):
            with open(path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                self.wfile.write(content)
        elif path.endswith('.wasm.gz'):
            with open(path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/wasm')
                self.end_headers()
                self.wfile.write(content)
        elif path.endswith('.gz'):
            with open(path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-Type',self.guess_type(path))
                self.end_headers()
                self.wfile.write(content)
        else:
            super().do_GET()

async def start_server_fix(BUILD_DIRECTORY):
    # Configuration
    PORT = 8000  # Port to serve the WebGL build
    BUILD_DIRECTORY = r"C:\Users\Sharky\iVISPAR_dev\iVISPAR"  # Replace with the path to your WebGL build folder

    # Change working directory to the WebGL build folder
    os.chdir(BUILD_DIRECTORY)

    # Create the handler
    Handler = GzipRequestHandler

    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving Unity WebGL on http://localhost:{PORT}")
        print("Opening the web app in your default browser...")
        webbrowser.open(f"http://localhost:{PORT}")  # Automatically open in the browser
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")
            httpd.server_close()

def run_socketserver_in_background(BUILD_DIRECTORY):
    # Start the server in a background thread
    server_thread = threading.Thread(target=lambda: asyncio.run(start_server_fix(BUILD_DIRECTORY)), daemon=True)
    server_thread.start()
    logging.info("Server started in the background.")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    webApp_dir = os.path.join(base_dir, 'iVISPAR')

    #Run the server in the background
    #run_socketserver_in_background(webApp_dir)
    #start_server_fix(webApp_dir)
    PORT = 8000  # Port to serve the WebGL build
    BUILD_DIRECTORY = r"C:\Users\Sharky\iVISPAR_dev"  # Replace with the path to your WebGL build folder

    # Change working directory to the WebGL build folder
    os.chdir(webApp_dir)

    # Create the handler
    #Handler = http.server.SimpleHTTPRequestHandler
    Handler = GzipRequestHandler
    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving Unity WebGL on http://localhost:{PORT}")
        print("Opening the web app in your default browser...")
        webbrowser.open(f"http://localhost:{PORT}")  # Automatically open in the browser
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")
            httpd.server_close()
    while True:
        pass
