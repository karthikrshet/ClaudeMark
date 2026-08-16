"""Standalone runner for ClaudeMark web server."""

import sys
from pathlib import Path
from http.server import HTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claudemark.server import ClaudeMarkHandler

def main():
    host = "127.0.0.1"
    port = 8888
    HTTPServer.allow_reuse_address = True
    server = HTTPServer((host, port), ClaudeMarkHandler)
    print(f"ClaudeMark Server listening on http://{host}:{port}/", flush=True)
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
