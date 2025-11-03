"""Simple controller to execute cryptographic test routines.

This module provides a minimal in-app replacement for the previous
external `crypto_core` dependency. It generates synthetic performance
metrics suitable for demoing the Django app without external packages.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import random

from .interfaces import CryptoResult


class TestController:
    """Run mock cryptographic operations and produce timing/memory metrics."""

    def run_test(self, algorithm: str, operation: str, message_size: int) -> CryptoResult:
        # Generate deterministic-ish pseudo metrics for repeatability
        seed_value = hash((algorithm, operation, int(message_size))) & 0xFFFFFFFF
        rng = random.Random(seed_value)

        # Simulate execution characteristics
        base_time_ms = {
            "ecc": 0.6,
            "dilithium": 1.0,
        }.get(algorithm, 0.8)

        op_factor = {
            "keygen": 2.2,
            "sign": 1.4,
            "verify": 1.0,
        }.get(operation, 1.0)

        size_factor = max(1.0, message_size / 256.0)

        jitter = rng.uniform(0.85, 1.15)
        execution_time_ms = round(base_time_ms * op_factor * size_factor * 10.0 * jitter, 4)

        base_mem_kb = 220.0 if algorithm == "dilithium" else 140.0
        memory_usage_kb = round(base_mem_kb * (0.9 + 0.2 * rng.random()) * (1.0 + 0.05 * (size_factor - 1.0)), 3)

        return CryptoResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            algorithm=algorithm,
            operation=operation,
            message_size=message_size,
            execution_time_ms=execution_time_ms,
            memory_usage_kb=memory_usage_kb,
            status="success",
            error_message=None,
        )


