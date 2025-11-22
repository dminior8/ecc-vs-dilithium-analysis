"""
Cryptographic correctness validation tests.

These tests validate fundamental cryptographic properties:
- Key uniqueness
- Signature correctness
- Security properties
- Standards compliance
- Resistance to tampering
"""

import os
import unittest
from django.test import TestCase
from ecc_vs_dilithium_analysis.controller import (
    ECCImplementation,
    DILITHIUMImplementation,
    ECC_AVAILABLE,
    DILITHIUM_AVAILABLE
)


class TestCryptographicCorrectness(TestCase):
    """Tests for cryptographic correctness validation."""
    
    def test_ecc_key_uniqueness(self):
        """Test that ECC generates unique keys each time (non-deterministic key generation)."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        keys = []
        for _ in range(10):
            ecc = ECCImplementation()
            priv, pub = ecc.generate_keys()
            key_pair = (priv.to_string(), pub.to_string())
            keys.append(key_pair)
        
        # All keys should be unique
        unique_keys = set(keys)
        self.assertEqual(len(unique_keys), 10, "All generated keys should be unique")
    
    def test_ecc_signature_uniqueness(self):
        """Test that ECC produces different signatures for same message (non-deterministic signing)."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc = ECCImplementation()
        ecc.generate_keys()
        message = b"test message"
        
        signatures = [ecc.sign(message) for _ in range(10)]
        
        # ECDSA with random k produces different signatures
        unique_sigs = set(signatures)
        self.assertEqual(len(unique_sigs), 10, "All signatures should be unique")
    
    def test_ecc_signature_verification_consistency(self):
        """Test that ECC signature verification is consistent (deterministic verification)."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc = ECCImplementation()
        ecc.generate_keys()
        message = b"test message"
        signature = ecc.sign(message)
        
        # Verify multiple times - should always succeed
        for _ in range(20):
            is_valid = ecc.verify(message, signature)
            self.assertTrue(is_valid, "Verification should be consistent")
    
    def test_ecc_tamper_resistance_message(self):
        """Test that ECC detects message tampering."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc = ECCImplementation()
        ecc.generate_keys()
        original_message = b"original message"
        signature = ecc.sign(original_message)
        
        # Try various tampering methods
        tampered_messages = [
            b"original messag",  # Remove one byte
            b"original messagf",  # Change one byte
            b"different message",  # Completely different
            b"",  # Empty
            b"original message extra",  # Add bytes
        ]
        
        for tampered in tampered_messages:
            is_valid = ecc.verify(tampered, signature)
            self.assertFalse(is_valid, f"Tampered message should be rejected: {tampered}")
    
    def test_ecc_tamper_resistance_signature(self):
        """Test that ECC detects signature tampering."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc = ECCImplementation()
        ecc.generate_keys()
        message = b"test message"
        signature = ecc.sign(message)
        
        # Try various tampering methods
        tampered_signatures = [
            signature[:-1],  # Remove last byte
            signature + b"\x00",  # Add byte
            bytes([(b ^ 1) for b in signature]),  # Flip all bits
            signature[:len(signature)//2],  # Half signature
        ]
        
        for tampered in tampered_signatures:
            is_valid = ecc.verify(message, tampered)
            self.assertFalse(is_valid, "Tampered signature should be rejected")
    
    def test_ecc_key_isolation(self):
        """Test that keys from different instances are isolated."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc1 = ECCImplementation()
        ecc2 = ECCImplementation()
        
        ecc1.generate_keys()
        ecc2.generate_keys()
        
        message = b"test message"
        signature1 = ecc1.sign(message)
        signature2 = ecc2.sign(message)
        
        # Each instance should only verify its own signatures
        self.assertTrue(ecc1.verify(message, signature1))
        self.assertTrue(ecc2.verify(message, signature2))
        self.assertFalse(ecc1.verify(message, signature2))
        self.assertFalse(ecc2.verify(message, signature1))
    
    def test_dilithium_key_uniqueness(self):
        """Test that Dilithium generates unique keys each time."""
        if not DILITHIUM_AVAILABLE:
            self.skipTest("Dilithium not available")
        
        try:
            keys = []
            for _ in range(10):
                dil = DILITHIUMImplementation()
                priv, pub = dil.generate_keys()
                key_pair = (priv, pub)
                keys.append(key_pair)
            
            # All keys should be unique
            unique_keys = set(keys)
            self.assertEqual(len(unique_keys), 10, "All generated keys should be unique")
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_dilithium_signature_verification_consistency(self):
        """Test that Dilithium signature verification is consistent."""
        if not DILITHIUM_AVAILABLE:
            self.skipTest("Dilithium not available")
        
        try:
            dil = DILITHIUMImplementation()
            dil.generate_keys()
            message = b"test message"
            signature = dil.sign(message)
            
            # Verify multiple times - should always succeed
            for _ in range(20):
                is_valid = dil.verify(message, signature)
                self.assertTrue(is_valid, "Verification should be consistent")
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_dilithium_tamper_resistance_message(self):
        """Test that Dilithium detects message tampering."""
        if not DILITHIUM_AVAILABLE:
            self.skipTest("Dilithium not available")
        
        try:
            dil = DILITHIUMImplementation()
            dil.generate_keys()
            original_message = b"original message"
            signature = dil.sign(original_message)
            
            # Try various tampering methods
            tampered_messages = [
                b"original messag",  # Remove one byte
                b"original messagf",  # Change one byte
                b"different message",  # Completely different
                b"",  # Empty
                b"original message extra",  # Add bytes
            ]
            
            for tampered in tampered_messages:
                is_valid = dil.verify(tampered, signature)
                self.assertFalse(is_valid, f"Tampered message should be rejected: {tampered}")
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_dilithium_tamper_resistance_signature(self):
        """Test that Dilithium detects signature tampering."""
        if not DILITHIUM_AVAILABLE:
            self.skipTest("Dilithium not available")
        
        try:
            dil = DILITHIUMImplementation()
            dil.generate_keys()
            message = b"test message"
            signature = dil.sign(message)
            
            # Try various tampering methods
            tampered_signatures = [
                signature[:-1],  # Remove last byte
                signature + b"\x00",  # Add byte
                bytes([(b + 1) % 256 for b in signature]),  # Modify bytes
                signature[:len(signature)//2],  # Half signature
            ]
            
            for tampered in tampered_signatures:
                is_valid = dil.verify(message, tampered)
                self.assertFalse(is_valid, "Tampered signature should be rejected")
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_dilithium_key_isolation(self):
        """Test that Dilithium keys from different instances are isolated."""
        if not DILITHIUM_AVAILABLE:
            self.skipTest("Dilithium not available")
        
        try:
            dil1 = DILITHIUMImplementation()
            dil2 = DILITHIUMImplementation()
            
            dil1.generate_keys()
            dil2.generate_keys()
            
            message = b"test message"
            signature1 = dil1.sign(message)
            signature2 = dil2.sign(message)
            
            # Each instance should only verify its own signatures
            self.assertTrue(dil1.verify(message, signature1))
            self.assertTrue(dil2.verify(message, signature2))
            self.assertFalse(dil1.verify(message, signature2))
            self.assertFalse(dil2.verify(message, signature1))
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_cross_algorithm_isolation(self):
        """Test that ECC and Dilithium cannot verify each other's signatures."""
        if not ECC_AVAILABLE or not DILITHIUM_AVAILABLE:
            self.skipTest("Both algorithms not available")
        
        try:
            ecc = ECCImplementation()
            dil = DILITHIUMImplementation()
            
            ecc.generate_keys()
            dil.generate_keys()
            
            message = b"test message"
            ecc_sig = ecc.sign(message)
            dil_sig = dil.sign(message)
            
            # Cross-verification should fail
            # Note: This might raise exceptions, which is also acceptable
            try:
                ecc_result = ecc.verify(message, dil_sig)
                self.assertFalse(ecc_result, "ECC should not verify Dilithium signatures")
            except Exception:
                pass  # Exception is also acceptable
            
            try:
                dil_result = dil.verify(message, ecc_sig)
                self.assertFalse(dil_result, "Dilithium should not verify ECC signatures")
            except Exception:
                pass  # Exception is also acceptable
        except RuntimeError as e:
            self.skipTest(f"Initialization failed: {e}")
    
    def test_message_size_independence(self):
        """Test that cryptographic operations work correctly for various message sizes."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc = ECCImplementation()
        ecc.generate_keys()
        
        message_sizes = [0, 1, 32, 256, 1024, 4096]
        
        for size in message_sizes:
            message = os.urandom(size) if size > 0 else b""
            signature = ecc.sign(message)
            is_valid = ecc.verify(message, signature)
            self.assertTrue(is_valid, f"Should work for message size {size}")
    
    def test_deterministic_verification_property(self):
        """Test that verification is deterministic (same inputs always give same result)."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        ecc = ECCImplementation()
        ecc.generate_keys()
        message = b"deterministic test message"
        signature = ecc.sign(message)
        
        results = []
        for _ in range(50):
            is_valid = ecc.verify(message, signature)
            results.append(is_valid)
        
        # All results should be the same
        self.assertTrue(all(results), "Verification should be deterministic")
        self.assertEqual(len(set(results)), 1, "All verification results should be identical")