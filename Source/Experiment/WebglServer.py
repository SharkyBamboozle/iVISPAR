import http.server
import socketserver
import os

import threading


# Configuration
PORT = 8000  # Port to serve the WebGL build
BUILD_DIRECTORY = r"C:\Users\Sharky\RIPPLE\iVISPAR"  # Replace with the path to your WebGL build folder

# Change working directory to the WebGL build folder
os.chdir(BUILD_DIRECTORY)

# Create the handler
Handler = http.server.SimpleHTTPRequestHandler

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving Unity WebGL on http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        httpd.server_close()




def start_server():
    # Configuration
    PORT = 8000  # Port to serve the WebGL build
    BUILD_DIRECTORY = r"C:\Users\Sharky\RIPPLE\iVISPAR"  # Replace with the path to your WebGL build folder

    # Change working directory to the WebGL build folder
    os.chdir(BUILD_DIRECTORY)

    # Create the handler
    Handler = http.server.SimpleHTTPRequestHandler

    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving Unity WebGL on http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")
            httpd.server_close()

def run_WebGL_server_in_background():
    # Start the server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print("Server started in the background.")
