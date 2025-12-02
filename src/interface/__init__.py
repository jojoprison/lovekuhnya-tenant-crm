"""Interface layer (adapters).

Currently exposes HTTP API built on top of existing src.api.v1 routers.
This keeps behavior unchanged while making the layer boundary explicit.
"""

from src.api.v1 import router as router

__all__ = ["router"]
