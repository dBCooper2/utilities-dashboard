#!/usr/bin/env python3
"""
Simple HTTP server to serve GeoJSON files.
This is a fallback solution while the backend API is being fixed.
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

PORT = 8080
GEOJSON_DIR = "frontend/public/geojson"

class GeoJSONHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving GeoJSON files with CORS headers"""
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Add CORS headers to all responses
        self.send_cors_headers()
        
        # Handle specific paths
        if path == '/geojson' or path == '/geojson/':
            self.list_geojson_files()
        elif path.startswith('/geojson/'):
            # Extract the filename from the path
            filename = path.split('/geojson/')[1]
            self.serve_geojson_file(filename)
        else:
            # Default handler for other paths
            super().do_GET()
    
    def send_cors_headers(self):
        """Add CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-Length', '0')
        self.end_headers()
    
    def list_geojson_files(self):
        """Return a list of available GeoJSON files"""
        try:
            files = [f for f in os.listdir(GEOJSON_DIR) if f.endswith('.geojson') or f.endswith('.json')]
            response = {
                'status': 'success',
                'files': files,
                'count': len(files),
                'base_url': f'http://localhost:{PORT}/geojson/'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
        except Exception as e:
            self.send_error(500, f"Error listing GeoJSON files: {str(e)}")
    
    def serve_geojson_file(self, filename):
        """Serve a specific GeoJSON file"""
        file_path = os.path.join(GEOJSON_DIR, filename)
        
        if not os.path.exists(file_path):
            self.send_error(404, f"File not found: {filename}")
            return
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/geo+json')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error serving file {filename}: {str(e)}")

def run_server():
    """Start the HTTP server"""
    # Create the GeoJSON directory if it doesn't exist
    os.makedirs(GEOJSON_DIR, exist_ok=True)
    
    # Check if we have any GeoJSON files
    files = [f for f in os.listdir(GEOJSON_DIR) if f.endswith('.geojson') or f.endswith('.json')]
    if not files:
        print(f"Warning: No GeoJSON files found in {GEOJSON_DIR}")
    else:
        print(f"Found {len(files)} GeoJSON files in {GEOJSON_DIR}")
        for f in files:
            print(f"  - {f}")
    
    # Set up the server
    handler = GeoJSONHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Starting GeoJSON server at http://localhost:{PORT}")
    print(f"GeoJSON files available at http://localhost:{PORT}/geojson/")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    run_server() 