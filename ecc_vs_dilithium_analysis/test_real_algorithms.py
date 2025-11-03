"""Test Cases for Real Cryptographic Algorithms

This module tests the actual implementations of ECC and Dilithium algorithms.
Run with: python manage.py shell < test_real_algorithms.py
Or: python -m pytest ecc_vs_dilithium_analysis/test_real_algorithms.py
"""

import unittest
from ecc_vs_dilithium_analysis.controller import ECCImplementation, DILITHIUMImplementation, TestController


class TestECCImplementation(unittest.TestCase):
    """Test ECC (NIST P-256) implementation."""
    
    def setUp(self):
        try:
            self.ecc = ECCImplementation()
        except ImportError as e:
            self.skipTest(f"ECC not available: {e}")
    
    def test_key_generation(self):
        """Test ECC key generation."""
        private_key, public_key = self.ecc.generate_keys()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        print("✅ ECC key generation passed")
    
    def test_sign_and_verify(self):
        """Test ECC signing and verification."""
        self.ecc.generate_keys()
        
        msg = b"test message"
        sig = self.ecc.sign(msg)
        
        # Verify correct message
        self.assertTrue(self.ecc.verify(msg, sig), "ECC verification failed for correct message")
        
        # Verify wrong message should fail
        self.assertFalse(self.ecc.verify(b"wrong message", sig), "ECC should fail for wrong message")
        
        print("✅ ECC sign/verify tests passed")
    
    def test_sign_requires_keys(self):
        """Test that signing requires keys to be generated."""
        ecc = ECCImplementation()
        with self.assertRaises(ValueError):
            ecc.sign(b"test")


class TestDILITHIUMImplementation(unittest.TestCase):
    """Test CRYSTALS-Dilithium (ML-DSA) implementation."""
    
    def setUp(self):
        try:
            self.dil = DILITHIUMImplementation()
        except ImportError as e:
            self.skipTest(f"Dilithium not available: {e}")
        except RuntimeError as e:
            self.skipTest(f"Dilithium initialization failed: {e}")
    
    def test_key_generation(self):
        """Test Dilithium key generation."""
        private_key, public_key = self.dil.generate_keys()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        print("✅ Dilithium key generation passed")
    
    def test_sign_and_verify(self):
        """Test Dilithium signing and verification."""
        self.dil.generate_keys()
        
        msg = b"test message"
        sig = self.dil.sign(msg)
        
        # Verify correct message
        self.assertTrue(self.dil.verify(msg, sig), "Dilithium verification failed for correct message")
        
        # Verify wrong message should fail
        self.assertFalse(self.dil.verify(b"wrong message", sig), "Dilithium should fail for wrong message")
        
        print("✅ Dilithium sign/verify tests passed")
    
    def test_sign_requires_keys(self):
        """Test that signing requires keys to be generated."""
        dil = DILITHIUMImplementation()
        with self.assertRaises(ValueError):
            dil.sign(b"test")


class TestTestController(unittest.TestCase):
    """Test TestController with real measurements."""
    
    def setUp(self):
        self.controller = TestController()
    
    def test_ecc_keygen(self):
        """Test ECC keygen with real measurement."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'keygen', 256)
        self.assertEqual(result.status, 'success')
        self.assertGreater(result.execution_time_ms, 0)
        print(f"✅ ECC KeyGen: {result.execution_time_ms:.2f} ms, {result.memory_usage_kb:.2f} KB")
    
    def test_dilithium_keygen(self):
        """Test Dilithium keygen with real measurement."""
        if 'dilithium' not in self.controller.algorithms:
            self.skipTest("Dilithium not available")
        
        result = self.controller.run_test('dilithium', 'keygen', 256)
        self.assertEqual(result.status, 'success')
        self.assertGreater(result.execution_time_ms, 0)
        print(f"✅ Dilithium KeyGen: {result.execution_time_ms:.2f} ms, {result.memory_usage_kb:.2f} KB")
    
    def test_ecc_sign(self):
        """Test ECC signing with real measurement."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'sign', 256)
        self.assertEqual(result.status, 'success')
        self.assertGreater(result.execution_time_ms, 0)
        print(f"✅ ECC Sign: {result.execution_time_ms:.2f} ms, {result.memory_usage_kb:.2f} KB")
    
    def test_dilithium_sign(self):
        """Test Dilithium signing with real measurement."""
        if 'dilithium' not in self.controller.algorithms:
            self.skipTest("Dilithium not available")
        
        result = self.controller.run_test('dilithium', 'sign', 256)
        self.assertEqual(result.status, 'success')
        self.assertGreater(result.execution_time_ms, 0)
        print(f"✅ Dilithium Sign: {result.execution_time_ms:.2f} ms, {result.memory_usage_kb:.2f} KB")
    
    def test_invalid_algorithm(self):
        """Test invalid algorithm handling."""
        result = self.controller.run_test('invalid', 'keygen', 256)
        self.assertEqual(result.status, 'failure')
        self.assertIsNotNone(result.error_message)


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Real Cryptographic Implementations")
    print("=" * 60)
    
    unittest.main(verbosity=2)

