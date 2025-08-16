import threading
from web_server import start_web_server

def keep_alive():
    """
    Start the keep-alive web server
    This helps keep the bot running on platforms like Render.com
    """
    try:
        start_web_server()
        print("Keep-alive system started successfully")
    except Exception as e:
        print(f"Error starting keep-alive system: {e}")

if __name__ == "__main__":
    keep_alive()
    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Keep-alive system stopped")
