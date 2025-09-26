"""
Test snippet for P14_TunnelManager functionality
"""

import time
import threading
import http.server
import socketserver
import traceback
from P14_TunnelManager import P14_TunnelManager


def test_callback(line: str) -> None:
    """Simple callback that prints log lines."""
    print(f"[TUNNEL LOG] {line}")


def run_test_server(port: int = 8000) -> None:
    """Run a simple HTTP server for testing."""
    try:
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"Test server running on port {port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Test server failed: {e}")


def main() -> None:
    """Test the P14_TunnelManager with a simple HTTP server."""
    server_thread = None

    try:
        # Start test server in background thread
        server_thread = threading.Thread(target=run_test_server, daemon=True)
        server_thread.start()

        # Give server time to start
        time.sleep(2)

        # Initialize tunnel manager
        tunnel_manager = P14_TunnelManager(callback=test_callback)

        # Create tunnel
        public_url = tunnel_manager.create_tunnel(8000)
        print(f"Public tunnel created: {public_url}")

        # Keep tunnel alive for testing
        print("Tunnel active for 10 seconds...")
        time.sleep(10)

        # Clean up
        tunnel_manager.kill_tunnels()
        print("Tunnels killed successfully")

    except Exception as e:
        print(f"Test failed: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
    finally:
        if server_thread and server_thread.is_alive():
            print("Test completed")


if __name__ == "__main__":
    main()