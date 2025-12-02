"""Application layer: use cases / services.

This layer contains:
- ports.py: Repository interfaces (protocols) for dependency inversion.
- Services are accessed directly from src.services to avoid circular imports.
"""

from src.application.ports import DealRepositoryProtocol, TaskRepositoryProtocol

__all__ = [
    "DealRepositoryProtocol",
    "TaskRepositoryProtocol",
]
