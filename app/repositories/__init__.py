"""
Repository Layer - Pure Database Operations

Repositories handle ONLY database queries and operations.
NO business logic, NO validation, NO conditional parameter checking.

Principles:
1. Accept typed parameters (date, UUID, etc.) - NOT strings
2. Return raw query objects or data
3. Let the caller (controller/service) handle validation
4. Keep it simple and focused on database operations
"""

from .base import BaseRepository
from .p2h_repository import P2HRepository
from .dashboard_repository import DashboardRepository
from .vehicle_repository import VehicleRepository

__all__ = [
    'BaseRepository',
    'P2HRepository',
    'DashboardRepository',
    'VehicleRepository',
]
