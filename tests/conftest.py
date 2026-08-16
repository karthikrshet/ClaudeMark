"""Pytest shared fixtures for ClaudeMark test suite."""

import threading
from http.server import ThreadingHTTPServer
import pytest

from claudemark.server import ClaudeMarkHandler


@pytest.fixture
def running_claudemark_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ClaudeMarkHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()
