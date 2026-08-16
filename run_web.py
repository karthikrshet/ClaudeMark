"""Standalone runner for ClaudeMark web server."""

import sys
from pathlib import Path
from http.server import ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claudemark.server import ClaudeMarkHandler

def main():
    host = "127.0.0.1"
    port = 8950
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer((host, port), ClaudeMarkHandler)
    server.daemon_threads = True
    print(f"ClaudeMark Server listening on http://{host}:{port}/", flush=True)
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
