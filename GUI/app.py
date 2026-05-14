import http.server
import socketserver
import webbrowser
import os

PORT = 9000

# Set the working directory to the GUI folder so we can serve its contents
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Check if the requested path is a real file (like /assets/styles.css)
        path = self.translate_path(self.path)
        if os.path.exists(path) and not os.path.isdir(path):
            super().do_GET()
        else:
            # Fallback to serving index.html for SPA routing (like /success)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
                
    def log_message(self, format, *args):
        # Suppress logging for cleaner terminal output
        pass

class ReusableServer(socketserver.TCPServer): 
    allow_reuse_address = True

if __name__ == "__main__":
    with ReusableServer(("", PORT), SPAHandler) as server:
        print(f"✅ Cinema Pro Frontend serving static files at http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        server.serve_forever()
