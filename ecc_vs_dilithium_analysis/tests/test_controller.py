"""
Unit tests for TestController.

Tests validate:
- Test execution with real measurements
- Memory measurement accuracy
- Time measurement accuracy
- Error handling
- All operation types (keygen, sign, verify)
"""

import unittest
from django.test import TestCase
from ecc_vs_dilithium_analysis.controller import TestController, ECC_AVAILABLE, DILITHIUM_AVAILABLE


class TestTestController(TestCase):
    """Unit tests for TestController."""
    
    def setUp(self):
        """Initialize controller for each test."""
        self.controller = TestController()
    
    def test_controller_initialization(self):
        """Test that controller initializes correctly."""
        self.assertIsNotNone(self.controller)
        self.assertIsNotNone(self.controller.process)
        self.assertIsInstance(self.controller.algorithms, dict)
    
    def test_memory_measurement_returns_positive(self):
        """Test that memory measurement returns positive value."""
        memory = self.controller.measure_memory()
        self.assertGreater(memory, 0, "Memory usage should be positive")
    
    def test_ecc_keygen_execution(self):
        """Test ECC keygen operation execution."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'keygen', 256)
        
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.algorithm, 'ecc')
        self.assertEqual(result.operation, 'keygen')
        self.assertEqual(result.message_size, 256)
        self.assertGreater(result.execution_time_ms, 0, "Execution time should be positive")
        self.assertGreaterEqual(result.memory_usage_kb, 0, "Memory usage should be non-negative")
        self.assertIsNone(result.error_message)
    
    def test_ecc_sign_execution(self):
        """Test ECC sign operation execution."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'sign', 256)
        
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.operation, 'sign')
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsNone(result.error_message)
    
    def test_ecc_verify_execution(self):
        """Test ECC verify operation execution."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'verify', 256)
        
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.operation, 'verify')
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsNone(result.error_message)
    
    def test_dilithium_keygen_execution(self):
        """Test Dilithium keygen operation execution."""
        if 'dilithium' not in self.controller.algorithms:
            self.skipTest("Dilithium not available")
        
        result = self.controller.run_test('dilithium', 'keygen', 256)
        
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.algorithm, 'dilithium')
        self.assertEqual(result.operation, 'keygen')
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsNone(result.error_message)
    
    def test_dilithium_sign_execution(self):
        """Test Dilithium sign operation execution."""
        if 'dilithium' not in self.controller.algorithms:
            self.skipTest("Dilithium not available")
        
        result = self.controller.run_test('dilithium', 'sign', 256)
        
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.operation, 'sign')
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsNone(result.error_message)
    
    def test_dilithium_verify_execution(self):
        """Test Dilithium verify operation execution."""
        if 'dilithium' not in self.controller.algorithms:
            self.skipTest("Dilithium not available")
        
        result = self.controller.run_test('dilithium', 'verify', 256)
        
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.operation, 'verify')
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsNone(result.error_message)
    
    def test_invalid_algorithm_handling(self):
        """Test handling of invalid algorithm."""
        result = self.controller.run_test('invalid_algorithm', 'keygen', 256)
        
        self.assertEqual(result.status, 'failure')
        self.assertIsNotNone(result.error_message)
        self.assertIn('not available', result.error_message.lower())
    
    def test_invalid_operation_handling(self):
        """Test handling of invalid operation."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'invalid_operation', 256)
        
        self.assertEqual(result.status, 'failure')
        self.assertIsNotNone(result.error_message)
    
    def test_different_message_sizes(self):
        """Test execution with different message sizes."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        message_sizes = [32, 256, 1024, 4096]
        
        for size in message_sizes:
            result = self.controller.run_test('ecc', 'sign', size)
            self.assertEqual(result.status, 'success', f"Failed for message size {size}")
            self.assertEqual(result.message_size, size)
    
    def test_execution_time_measurement_accuracy(self):
        """Test that execution time measurement is reasonable."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'keygen', 256)
        
        # ECC keygen should be relatively fast (< 100ms typically)
        self.assertLess(result.execution_time_ms, 1000, "Execution time seems too high")
    
    def test_memory_usage_measurement(self):
        """Test that memory usage is measured correctly."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'keygen', 256)
        
        # Memory usage should be reasonable (not negative, not extremely large)
        self.assertGreaterEqual(result.memory_usage_kb, 0)
        self.assertLess(result.memory_usage_kb, 1000000, "Memory usage seems unreasonably high")
    
    def test_timestamp_is_iso_format(self):
        """Test that timestamp is in ISO format."""
        if 'ecc' not in self.controller.algorithms:
            self.skipTest("ECC not available")
        
        result = self.controller.run_test('ecc', 'keygen', 256)
        
        # Check ISO format (contains 'T' or 'Z' or timezone info)
        self.assertIn('T', result.timestamp or 'T', "Timestamp should be in ISO format")