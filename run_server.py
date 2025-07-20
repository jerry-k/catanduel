#!/usr/bin/env python3
"""
Simple script to run the CatanDuel server.
Automatically finds an available port.
"""

import os
import sys
import socket

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.server import app

def find_free_port(start_port=5002):
    """Find the first available port starting from start_port."""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    # If no port found in range, use random
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

if __name__ == '__main__':
    port = find_free_port()
    print(f"\n🎲 Starting CatanDuel server on port {port}")
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print(f"📝 Press Ctrl+C to stop the server\n")
    
    try:
        app.run(debug=True, port=port, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thanks for playing CatanDuel!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("💡 Try running again or check if another server is running.")