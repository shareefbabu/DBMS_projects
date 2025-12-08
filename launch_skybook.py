"""
SkyBook Website Launcher
Automatically starts the API server and opens the website in your browser.
"""

import subprocess
import time
import webbrowser
import os
import sys
import socket

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for Windows console
        if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError) as e:
        # Silently fail if reconfigure not available or fails
        pass

def check_port_available(port=5000):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except socket.error:
        return False

def wait_for_server(port=5000, timeout=30):
    """Wait for the server to start"""
    print(f"[*] Waiting for API server to start on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('localhost', port))
            sock.close()
            print("[OK] API server is ready!")
            return True
        except socket.error:
            time.sleep(0.5)
    
    return False

def main():
    print("=" * 60)
    print("       SkyBook Website Launcher")
    print("=" * 60)
    
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    api_script = os.path.join(project_dir, "api_server.py")
    index_html = os.path.join(project_dir, "index.html")
    
    # Check if files exist
    if not os.path.exists(api_script):
        print("[ERROR] api_server.py not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not os.path.exists(index_html):
        print("[ERROR] index.html not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if port 5000 is already in use
    if not check_port_available(5000):
        print("[WARNING] Port 5000 is already in use.")
        print("The API server might already be running.")
        response = input("Do you want to open the website anyway? (y/n): ")
        if response.lower() == 'y':
            print("[*] Opening SkyBook website...")
            webbrowser.open(f"file:///{index_html}")
            print("\n[OK] Website opened in your browser!")
            print("If the website is not working, please check that api_server.py is running.")
        sys.exit(0)
    
    # Start the API server
    print("\n[*] Starting API server...")
    print(f"Running: python {api_script}")
    
    try:
        # Start the server in a new process (won't block this script)
        if sys.platform == 'win32':
            # Windows - use CREATE_NEW_CONSOLE to open in new window
            api_process = subprocess.Popen(
                [sys.executable, api_script],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=project_dir
            )
        else:
            # Unix-like systems
            api_process = subprocess.Popen(
                [sys.executable, api_script],
                cwd=project_dir
            )
        
        print(f"[OK] API server process started (PID: {api_process.pid})")
        
        # Wait for server to be ready
        if wait_for_server(5000, timeout=30):
            time.sleep(1)  # Give it one more second to fully initialize
            
            # Open the website in default browser
            print("\n[*] Opening SkyBook website in your browser...")
            webbrowser.open(f"file:///{index_html}")
            
            print("\n" + "=" * 60)
            print("       SkyBook is now running!")
            print("=" * 60)
            print(f"  API Server: http://localhost:5000")
            print(f"  Website: file:///{index_html}")
            print("\n  Important Notes:")
            print("   * The API server is running in a separate window")
            print("   * DO NOT close that window while using SkyBook")
            print("   * Close the API server window when you're done")
            print("   * You can close this window now")
            print("=" * 60)
            
            input("\nPress Enter to close this launcher...")
        else:
            print("[ERROR] API server failed to start within 30 seconds")
            print("Please check the API server window for error messages")
            api_process.terminate()
            input("Press Enter to exit...")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error starting API server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLauncher interrupted. Exiting...")
        sys.exit(0)
