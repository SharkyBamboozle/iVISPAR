import http.server
import socketserver
import os
import threading
import webbrowser
import time  # Example to show main script continuing work
import asyncio


async def start_server():
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
        print("Opening the web app in your default browser...")
        webbrowser.open(f"http://localhost:{PORT}")  # Automatically open in the browser
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")
            httpd.server_close()

def run_WebGL_server_in_background():
    # Start the server in a background thread
    server_thread = threading.Thread(target=lambda: asyncio.run(start_server()), daemon=True)
    server_thread.start()
    print("Server started in the background.")


if __name__ == "__main__":
    run_WebGL_server_in_background()

    # Continue running main script logic
    print("Main script is running while the server is in the background.")
    for i in range(10):
        print(f"Main script working... {i}")
        time.sleep(1)
