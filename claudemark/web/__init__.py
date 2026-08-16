"""ClaudeMark web user interface and REST API subpackage."""

from .app import (
    get_static_asset,
    handle_api_analyze,
    handle_api_diff,
    handle_api_normalize,
)

__all__ = [
    "get_static_asset",
    "handle_api_analyze",
    "handle_api_normalize",
    "handle_api_diff",
]
