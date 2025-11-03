"""Real cryptographic implementations for ECC and CRYSTALS-Dilithium.

This module provides actual implementations of cryptographic algorithms:
- ECC (NIST P-256) using FIPS 186-5 ECDSA
- CRYSTALS-Dilithium (ML-DSA) using FIPS 204

All measurements are real and performed on actual cryptographic operations.
"""

from __future__ import annotations

import time
import psutil
import os
from datetime import datetime, timezone
from typing import Optional

# ECC imports
try:
    from ecdsa import SigningKey, VerifyingKey, NIST256p
    import hashlib
    ECC_AVAILABLE = True
except ImportError:
    ECC_AVAILABLE = False

# Dilithium imports
try:
    import oqs
    DILITHIUM_AVAILABLE = True
except ImportError:
    DILITHIUM_AVAILABLE = False

from .interfaces import CryptoResult


class ECCImplementation:
    """FIPS 186-5 ECDSA implementation using NIST P-256 curve."""
    
    def __init__(self):
        if not ECC_AVAILABLE:
            raise ImportError("ecdsa library not available. Install with: pip install ecdsa")
        self.private_key: Optional[SigningKey] = None
        self.public_key: Optional[VerifyingKey] = None
    
    def generate_keys(self):
        """FIPS 186-5 ECDSA Key Generation on secp256r1 (P-256)."""
        self.private_key = SigningKey.generate(curve=NIST256p)
        self.public_key = self.private_key.get_verifying_key()
        return self.private_key, self.public_key
    
    def sign(self, message: bytes) -> bytes:
        """ECDSA SHA-256 Signing."""
        if not self.private_key:
            raise ValueError("Keys not generated. Call generate_keys() first.")
        return self.private_key.sign(message, hashfunc=hashlib.sha256)
    
    def verify(self, message: bytes, signature: bytes) -> bool:
        """ECDSA Signature Verification."""
        if not self.public_key:
            raise ValueError("Keys not generated. Call generate_keys() first.")
        try:
            self.public_key.verify(signature, message, hashfunc=hashlib.sha256)
            return True
        except Exception:
            return False


class DILITHIUMImplementation:
    """FIPS 204 ML-DSA Level 2 (128-bit security) implementation."""
    
    def __init__(self):
        if not DILITHIUM_AVAILABLE:
            raise ImportError(
                "liboqs-python not available. Install liboqs C library first, "
                "then: pip install liboqs-python"
            )
        try:
            # Try ML-DSA-2 (FIPS 204) or Dilithium2 (both are equivalent)
            # ML-DSA-2 corresponds to Dilithium2 (128-bit security)
            sig_name = None
            for name in ["Dilithium2", "ML-DSA-2"]:
                if name in oqs.get_enabled_sig_mechanisms():
                    sig_name = name
                    break
            
            if sig_name is None:
                available = oqs.get_enabled_sig_mechanisms()
                raise RuntimeError(
                    f"Dilithium2/ML-DSA-2 not available. Available: {available[:5]}"
                )
            
            self.sig = oqs.Signature(sig_name)
            self.private_key: Optional[bytes] = None
            self.public_key: Optional[bytes] = None
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Dilithium: {e}")
    
    def generate_keys(self):
        """ML-DSA Key Generation (FIPS 204)."""
        public_key, private_key = self.sig.generate_keypair()
        self.public_key = public_key
        self.private_key = private_key
        return private_key, public_key
    
    def sign(self, message: bytes) -> bytes:
        """ML-DSA Signature Generation."""
        if not self.private_key:
            raise ValueError("Keys not generated. Call generate_keys() first.")
        return self.sig.sign(message, self.private_key)
    
    def verify(self, message: bytes, signature: bytes) -> bool:
        """ML-DSA Signature Verification."""
        if not self.public_key:
            raise ValueError("Keys not generated. Call generate_keys() first.")
        try:
            is_valid = self.sig.verify(message, signature, self.public_key)
            return is_valid
        except Exception:
            return False


class TestController:
    """Controller for executing real cryptographic tests with actual measurements."""
    
    def __init__(self):
        self.algorithms = {}
        
        # Initialize ECC if available
        if ECC_AVAILABLE:
            try:
                self.algorithms['ecc'] = ECCImplementation()
            except Exception as e:
                print(f"Warning: ECC initialization failed: {e}")
        
        # Initialize Dilithium if available
        if DILITHIUM_AVAILABLE:
            try:
                self.algorithms['dilithium'] = DILITHIUMImplementation()
            except Exception as e:
                print(f"Warning: Dilithium initialization failed: {e}")
        
        self.process = psutil.Process(os.getpid())
    
    def measure_memory(self) -> float:
        """Measure actual memory usage in KB."""
        return self.process.memory_info().rss / 1024
    
    def run_test(self, algorithm: str, operation: str, message_size: int) -> CryptoResult:
        """Execute REAL cryptographic test with actual time and memory measurement."""
        if algorithm not in self.algorithms:
            available = list(self.algorithms.keys())
            error_msg = f"Algorithm '{algorithm}' not available. Available: {available}"
            if algorithm == 'ecc' and not ECC_AVAILABLE:
                error_msg += ". Install: pip install ecdsa"
            elif algorithm == 'dilithium' and not DILITHIUM_AVAILABLE:
                error_msg += ". Install liboqs C library and liboqs-python"
            
            return CryptoResult(
                timestamp=datetime.now(timezone.utc).isoformat(),
                algorithm=algorithm,
                operation=operation,
                message_size=message_size,
                execution_time_ms=0.0,
                memory_usage_kb=0.0,
                status='failure',
                error_message=error_msg
            )
        
        algo = self.algorithms[algorithm]
        test_message = os.urandom(message_size)
        
        memory_before = self.measure_memory()
        start_time = time.perf_counter()
        
        try:
            if operation == 'keygen':
                algo.generate_keys()
            elif operation == 'sign':
                if not algo.private_key:
                    algo.generate_keys()
                algo.sign(test_message)
            elif operation == 'verify':
                if not algo.private_key:
                    algo.generate_keys()
                signature = algo.sign(test_message)
                is_valid = algo.verify(test_message, signature)
                if not is_valid:
                    raise ValueError("Signature verification failed")
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            end_time = time.perf_counter()
            memory_after = self.measure_memory()
            
            execution_time_ms = (end_time - start_time) * 1000
            memory_usage_kb = max(0.0, memory_after - memory_before)
            
            return CryptoResult(
                timestamp=datetime.now(timezone.utc).isoformat(),
                algorithm=algorithm,
                operation=operation,
                message_size=message_size,
                execution_time_ms=round(execution_time_ms, 4),
                memory_usage_kb=round(memory_usage_kb, 3),
                status='success',
                error_message=None
            )
        
        except Exception as e:
            return CryptoResult(
                timestamp=datetime.now(timezone.utc).isoformat(),
                algorithm=algorithm,
                operation=operation,
                message_size=message_size,
                execution_time_ms=0.0,
                memory_usage_kb=0.0,
                status='failure',
                error_message=str(e)
            )
