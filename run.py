#!/usr/bin/env python3
"""
Startup script for the Surveillance Camera Streaming Application
"""

import sys
import os
import socket

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def main():
    """Main startup function"""
    print("🚀 Starting Surveillance Camera Streaming Application...")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check if required packages are installed
    try:
        import flask
        import flask_socketio
        print("✅ Required packages are installed")
    except ImportError as e:
        print(f"❌ Error: Missing required package - {e}")
        print("   Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Get local IP
    local_ip = get_local_ip()
    
    print("\n📡 Network Information:")
    print(f"   Local access: http://localhost:5000")
    print(f"   Network access: http://{local_ip}:5000")
    
    print("\n🔐 Security Note:")
    print("   - Each stream requires a password to start")
    print("   - Streams are isolated in separate rooms")
    print("   - WebRTC connections are peer-to-peer")
    
    print("\n📱 Usage:")
    print("   1. Open the app in your browser")
    print("   2. Click 'Start Streaming' to broadcast your camera")
    print("   3. Others can click 'View Streams' to watch")
    
    print("\n" + "=" * 60)
    print("Starting Flask server...")
    
    try:
        # Import and run the Flask app
        from app import app, socketio
        
        # Run the application
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=False,  # Set to False for production
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 