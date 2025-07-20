#!/usr/bin/env python3
"""
Simple script to run the CatanDuel UI server.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.server import app

if __name__ == '__main__':
    # Start on port 5555 for testing
    app.run(debug=True, port=5555, host='0.0.0.0')