"""Shared data interfaces for the ECC vs Dilithium app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CryptoResult:
    timestamp: str
    algorithm: str
    operation: str
    message_size: int
    execution_time_ms: float
    memory_usage_kb: float
    status: str
    error_message: Optional[str] = None


