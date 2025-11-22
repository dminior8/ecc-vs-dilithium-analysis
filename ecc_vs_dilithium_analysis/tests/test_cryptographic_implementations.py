"""
Unit tests for cryptographic implementations (ECC and Dilithium).

Tests validate:
- Key generation correctness
- Signing operations
- Verification operations
- Error handling
- Cryptographic properties
"""

import unittest
import os
from django.test import TestCase
from ecc_vs_dilithium_analysis.controller import (
    ECCImplementation,
    DILITHIUMImplementation,
    ECC_AVAILABLE,
    DILITHIUM_AVAILABLE
)


class TestECCImplementation(TestCase):
    """Unit tests for ECC (NIST P-256) implementation."""
    
    def setUp(self):
        """Initialize ECC instance for each test."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC library not available")
        self.ecc = ECCImplementation()
    
    def test_key_generation_creates_keys(self):
        """Test that key generation creates valid private and public keys."""
        private_key, public_key = self.ecc.generate_keys()
        
        self.assertIsNotNone(private_key, "Private key should not be None")
        self.assertIsNotNone(public_key, "Public key should not be None")
        self.assertEqual(self.ecc.private_key, private_key)
        self.assertEqual(self.ecc.public_key, public_key)
    
    def test_key_generation_produces_different_keys(self):
        """Test that each key generation produces different keys (non-deterministic)."""
        ecc1 = ECCImplementation()
        ecc2 = ECCImplementation()
        
        priv1, pub1 = ecc1.generate_keys()
        priv2, pub2 = ecc2.generate_keys()
        
        # Keys should be different (ECDSA uses random generation)
        self.assertNotEqual(priv1.to_string(), priv2.to_string())
        self.assertNotEqual(pub1.to_string(), pub2.to_string())
    
    def test_sign_requires_keys(self):
        """Test that signing fails if keys are not generated."""
        ecc = ECCImplementation()
        message = b"test message"
        
        with self.assertRaises(ValueError) as context:
            ecc.sign(message)
        
        self.assertIn("Keys not generated", str(context.exception))
    
    def test_sign_produces_signature(self):
        """Test that signing produces a valid signature."""
        self.ecc.generate_keys()
        message = b"test message"
        
        signature = self.ecc.sign(message)
        
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertGreater(len(signature), 0)
    
    def test_sign_produces_different_signatures(self):
        """Test that signing the same message multiple times produces different signatures (ECDSA non-deterministic)."""
        self.ecc.generate_keys()
        message = b"test message"
        
        sig1 = self.ecc.sign(message)
        sig2 = self.ecc.sign(message)
        
        # ECDSA with random k produces different signatures
        self.assertNotEqual(sig1, sig2)
    
    def test_verify_valid_signature(self):
        """Test that verification succeeds for valid signatures."""
        self.ecc.generate_keys()
        message = b"test message"
        signature = self.ecc.sign(message)
        
        is_valid = self.ecc.verify(message, signature)
        
        self.assertTrue(is_valid, "Valid signature should verify correctly")
    
    def test_verify_invalid_signature_fails(self):
        """Test that verification fails for invalid signatures."""
        self.ecc.generate_keys()
        message = b"test message"
        signature = self.ecc.sign(message)
        
        # Modify signature (flip last bit)
        invalid_sig = signature[:-1] + bytes([signature[-1] ^ 1])
        
        is_valid = self.ecc.verify(message, invalid_sig)
        
        self.assertFalse(is_valid, "Invalid signature should be rejected")
    
    def test_verify_wrong_message_fails(self):
        """Test that verification fails when message is modified."""
        self.ecc.generate_keys()
        original_message = b"test message"
        signature = self.ecc.sign(original_message)
        
        modified_message = b"different message"
        is_valid = self.ecc.verify(modified_message, signature)
        
        self.assertFalse(is_valid, "Modified message should be rejected")
    
    def test_verify_empty_message(self):
        """Test signing and verifying empty message."""
        self.ecc.generate_keys()
        empty_message = b""
        
        signature = self.ecc.sign(empty_message)
        is_valid = self.ecc.verify(empty_message, signature)
        
        self.assertTrue(is_valid, "Empty message should be signable and verifiable")
    
    def test_verify_large_message(self):
        """Test signing and verifying large message (4096 bytes)."""
        self.ecc.generate_keys()
        large_message = os.urandom(4096)
        
        signature = self.ecc.sign(large_message)
        is_valid = self.ecc.verify(large_message, signature)
        
        self.assertTrue(is_valid, "Large message should be signable and verifiable")
    
    def test_verify_requires_keys(self):
        """Test that verification fails if keys are not generated."""
        ecc = ECCImplementation()
        message = b"test message"
        signature = b"fake signature"
        
        with self.assertRaises(ValueError) as context:
            ecc.verify(message, signature)
        
        self.assertIn("Keys not generated", str(context.exception))
    
    def test_cryptographic_correctness_deterministic_verification(self):
        """Test that same message+signature always verifies correctly (deterministic verification)."""
        self.ecc.generate_keys()
        message = b"cryptographic test message"
        signature = self.ecc.sign(message)
        
        # Verify multiple times - should always succeed
        for _ in range(10):
            is_valid = self.ecc.verify(message, signature)
            self.assertTrue(is_valid, "Verification should be deterministic")
    
    def test_cryptographic_correctness_key_isolation(self):
        """Test that keys from different instances cannot verify each other's signatures."""
        ecc1 = ECCImplementation()
        ecc2 = ECCImplementation()
        
        ecc1.generate_keys()
        ecc2.generate_keys()
        
        message = b"test message"
        signature = ecc1.sign(message)
        
        # ECC2 should not be able to verify ECC1's signature
        is_valid = ecc2.verify(message, signature)
        self.assertFalse(is_valid, "Keys should be isolated between instances")


class TestDILITHIUMImplementation(TestCase):
    """Unit tests for CRYSTALS-Dilithium (ML-DSA) implementation."""
    
    def setUp(self):
        """Initialize Dilithium instance for each test."""
        if not DILITHIUM_AVAILABLE:
            self.skipTest("Dilithium library not available")
        try:
            self.dil = DILITHIUMImplementation()
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_key_generation_creates_keys(self):
        """Test that key generation creates valid private and public keys."""
        private_key, public_key = self.dil.generate_keys()
        
        self.assertIsNotNone(private_key, "Private key should not be None")
        self.assertIsNotNone(public_key, "Public key should not be None")
        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        self.assertGreater(len(private_key), 0)
        self.assertGreater(len(public_key), 0)
    
    def test_key_generation_produces_different_keys(self):
        """Test that each key generation produces different keys."""
        dil1 = DILITHIUMImplementation()
        dil2 = DILITHIUMImplementation()
        
        priv1, pub1 = dil1.generate_keys()
        priv2, pub2 = dil2.generate_keys()
        
        # Keys should be different
        self.assertNotEqual(priv1, priv2)
        self.assertNotEqual(pub1, pub2)
    
    def test_key_sizes_are_correct(self):
        """Test that Dilithium2 keys have expected sizes (FIPS 204 ML-DSA-2)."""
        private_key, public_key = self.dil.generate_keys()
        
        # ML-DSA-2 (Dilithium2) key sizes
        # Public key: ~1312 bytes, Private key: ~2528 bytes
        self.assertGreaterEqual(len(public_key), 1000, "Public key too small")
        self.assertLessEqual(len(public_key), 2000, "Public key too large")
        self.assertGreaterEqual(len(private_key), 2000, "Private key too small")
        self.assertLessEqual(len(private_key), 3000, "Private key too large")
    
    def test_sign_requires_keys(self):
        """Test that signing fails if keys are not generated."""
        dil = DILITHIUMImplementation()
        message = b"test message"
        
        with self.assertRaises(ValueError) as context:
            dil.sign(message)
        
        self.assertIn("Keys not generated", str(context.exception))
    
    def test_sign_produces_signature(self):
        """Test that signing produces a valid signature."""
        self.dil.generate_keys()
        message = b"test message"
        
        signature = self.dil.sign(message)
        
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertGreater(len(signature), 0)
    
    def test_signature_size_is_correct(self):
        """Test that Dilithium2 signatures have expected size (FIPS 204 ML-DSA-2)."""
        self.dil.generate_keys()
        message = b"test message"
        signature = self.dil.sign(message)
        
        # ML-DSA-2 signature size: ~2420 bytes
        self.assertGreaterEqual(len(signature), 2000, "Signature too small")
        self.assertLessEqual(len(signature), 3000, "Signature too large")
    
    def test_verify_valid_signature(self):
        """Test that verification succeeds for valid signatures."""
        self.dil.generate_keys()
        message = b"test message"
        signature = self.dil.sign(message)
        
        is_valid = self.dil.verify(message, signature)
        
        self.assertTrue(is_valid, "Valid signature should verify correctly")
    
    def test_verify_invalid_signature_fails(self):
        """Test that verification fails for invalid signatures."""
        self.dil.generate_keys()
        message = b"test message"
        signature = self.dil.sign(message)
        
        # Modify signature
        invalid_sig = signature[:-1] + bytes([(signature[-1] + 1) % 256])
        
        is_valid = self.dil.verify(message, invalid_sig)
        
        self.assertFalse(is_valid, "Invalid signature should be rejected")
    
    def test_verify_wrong_message_fails(self):
        """Test that verification fails when message is modified."""
        self.dil.generate_keys()
        original_message = b"test message"
        signature = self.dil.sign(original_message)
        
        modified_message = b"different message"
        is_valid = self.dil.verify(modified_message, signature)
        
        self.assertFalse(is_valid, "Modified message should be rejected")
    
    def test_verify_empty_message(self):
        """Test signing and verifying empty message."""
        self.dil.generate_keys()
        empty_message = b""
        
        signature = self.dil.sign(empty_message)
        is_valid = self.dil.verify(empty_message, signature)
        
        self.assertTrue(is_valid, "Empty message should be signable and verifiable")
    
    def test_verify_large_message(self):
        """Test signing and verifying large message (4096 bytes)."""
        self.dil.generate_keys()
        large_message = os.urandom(4096)
        
        signature = self.dil.sign(large_message)
        is_valid = self.dil.verify(large_message, signature)
        
        self.assertTrue(is_valid, "Large message should be signable and verifiable")
    
    def test_verify_requires_keys(self):
        """Test that verification fails if keys are not generated."""
        dil = DILITHIUMImplementation()
        message = b"test message"
        signature = b"fake signature"
        
        with self.assertRaises(ValueError) as context:
            dil.verify(message, signature)
        
        self.assertIn("Keys not generated", str(context.exception))
    
    def test_cryptographic_correctness_deterministic_verification(self):
        """Test that same message+signature always verifies correctly."""
        self.dil.generate_keys()
        message = b"cryptographic test message"
        signature = self.dil.sign(message)
        
        # Verify multiple times - should always succeed
        for _ in range(10):
            is_valid = self.dil.verify(message, signature)
            self.assertTrue(is_valid, "Verification should be deterministic")
    
    def test_cryptographic_correctness_key_isolation(self):
        """Test that keys from different instances cannot verify each other's signatures."""
        dil1 = DILITHIUMImplementation()
        dil2 = DILITHIUMImplementation()
        
        dil1.generate_keys()
        dil2.generate_keys()
        
        message = b"test message"
        signature = dil1.sign(message)
        
        # DIL2 should not be able to verify DIL1's signature
        is_valid = dil2.verify(message, signature)
        self.assertFalse(is_valid, "Keys should be isolated between instances")
    
    def test_cryptographic_correctness_signature_uniqueness(self):
        """Test that signatures are unique (even if deterministic, should vary with message)."""
        self.dil.generate_keys()
        
        messages = [b"message1", b"message2", b"message3"]
        signatures = [self.dil.sign(msg) for msg in messages]
        
        # All signatures should be different
        self.assertEqual(len(signatures), len(set(signatures)), "Signatures should be unique per message")