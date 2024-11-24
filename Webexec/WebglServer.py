import http.server
import socketserver
import os

# Configuration
PORT = 8000  # Port to serve the WebGL build
#BUILD_DIRECTORY = ""  # Replace with the path to your WebGL build folder

# Change working directory to the WebGL build folder
#os.chdir(BUILD_DIRECTORY)

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