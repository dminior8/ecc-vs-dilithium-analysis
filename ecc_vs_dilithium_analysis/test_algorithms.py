"""Test Cases for Cryptographic Algorithms"""
import unittest
from ecc_vs_dilithium_analysis.interfaces import CryptoResult
from crypto_core.ecc_implementation import ECCImplementation
from crypto_core.dilithium_implementation import DILITHIUMImplementation


class TestECCImplementation(unittest.TestCase):
    """Tests for ECC implementation."""

    def setUp(self):
        """Initialize ECC instance."""
        self.algo = ECCImplementation()

    def test_algorithm_name(self):
        """Test that algorithm has correct name."""
        self.assertEqual(self.algo.algorithm_name, "ECC (NIST P-256)")

    def test_generate_keys(self):
        """Test key generation."""
        private_key, public_key = self.algo.generate_keys()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertEqual(self.algo.private_key, private_key)
        self.assertEqual(self.algo.public_key, public_key)

    def test_sign_requires_keys(self):
        """Test that signing requires generated keys."""
        with self.assertRaises(ValueError):
            self.algo.sign(b"test message")

    def test_sign_message(self):
        """Test message signing."""
        self.algo.generate_keys()
        message = b"test message"
        signature = self.algo.sign(message)

        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertGreater(len(signature), 0)

    def test_verify_valid_signature(self):
        """Test verification of valid signature."""
        self.algo.generate_keys()
        message = b"test message"
        signature = self.algo.sign(message)

        is_valid = self.algo.verify(message, signature)
        self.assertTrue(is_valid)

    def test_verify_invalid_signature(self):
        """Test verification rejects invalid signature."""
        self.algo.generate_keys()
        message = b"test message"
        signature = self.algo.sign(message)

        # Modify signature
        invalid_signature = signature[:-1] + bytes([(signature[-1] ^ 1)])

        is_valid = self.algo.verify(message, invalid_signature)
        self.assertFalse(is_valid)

    def test_verify_wrong_message(self):
        """Test that verification fails with wrong message."""
        self.algo.generate_keys()
        message = b"test message"
        signature = self.algo.sign(message)

        wrong_message = b"different message"
        is_valid = self.algo.verify(wrong_message, signature)
        self.assertFalse(is_valid)

    def test_key_sizes(self):
        """Test key size information."""
        sizes = self.algo.get_key_size()

        self.assertIn('private_key', sizes)
        self.assertIn('public_key', sizes)
        self.assertIn('signature', sizes)

        self.assertEqual(sizes['private_key'], 32)
        self.assertEqual(sizes['public_key'], 64)
        self.assertEqual(sizes['signature'], 64)


class TestDilithiumImplementation(unittest.TestCase):
    """Tests for CRYSTALS-Dilithium implementation."""

    def setUp(self):
        """Initialize Dilithium instance."""
        self.algo = DILITHIUMImplementation()

    def test_algorithm_name(self):
        """Test that algorithm has correct name."""
        self.assertEqual(self.algo.algorithm_name, "CRYSTALS-Dilithium")

    def test_generate_keys(self):
        """Test key generation."""
        private_key, public_key = self.algo.generate_keys()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertIsInstance(private_key, dict)
        self.assertIsInstance(public_key, dict)

    def test_sign_message(self):
        """Test message signing."""
        self.algo.generate_keys()
        message = b"test message"
        signature = self.algo.sign(message)

        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertEqual(len(signature), 2044)

    def test_verify_signature(self):
        """Test signature verification."""
        self.algo.generate_keys()
        message = b"test message"
        signature = self.algo.sign(message)

        is_valid = self.algo.verify(message, signature)
        self.assertTrue(is_valid)

    def test_key_sizes(self):
        """Test key size information."""
        sizes = self.algo.get_key_size()

        self.assertEqual(sizes['private_key'], 2528)
        self.assertEqual(sizes['public_key'], 1312)
        self.assertEqual(sizes['signature'], 2044)


class TestCryptoResult(unittest.TestCase):
    """Tests for CryptoResult data class."""

    def test_result_creation(self):
        """Test CryptoResult creation."""
        result = CryptoResult(
            timestamp="2025-11-03T18:00:00Z",
            algorithm="ecc",
            operation="keygen",
            message_size=256,
            execution_time_ms=2.34,
            memory_usage_kb=512,
            status="success"
        )

        self.assertEqual(result.algorithm, "ecc")
        self.assertEqual(result.operation, "keygen")
        self.assertEqual(result.execution_time_ms, 2.34)
        self.assertEqual(result.status, "success")

    def test_result_to_dict(self):
        """Test conversion to dictionary."""
        result = CryptoResult(
            timestamp="2025-11-03T18:00:00Z",
            algorithm="ecc",
            operation="keygen",
            message_size=256,
            execution_time_ms=2.34,
            memory_usage_kb=512,
            status="success"
        )

        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['algorithm'], "ecc")
        self.assertEqual(result_dict['operation'], "keygen")


if __name__ == '__main__':
    unittest.main()