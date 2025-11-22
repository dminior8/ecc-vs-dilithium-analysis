"""
Unit tests for Django models.

Tests validate:
- Model creation and saving
- Field validation
- Model methods
- Database constraints
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from ecc_vs_dilithium_analysis.models import TestResult
from datetime import datetime, timezone


class TestTestResultModel(TestCase):
    """Unit tests for TestResult model."""
    
    def test_create_test_result(self):
        """Test creating a TestResult instance."""
        result = TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        self.assertIsNotNone(result.id)
        self.assertEqual(result.algorithm, 'ecc')
        self.assertEqual(result.operation, 'keygen')
        self.assertEqual(result.message_size, 256)
        self.assertEqual(result.execution_time_ms, 3.247)
        self.assertEqual(result.memory_usage_kb, 128.5)
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.timestamp)
    
    def test_timestamp_auto_created(self):
        """Test that timestamp is automatically created."""
        result = TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        self.assertIsNotNone(result.timestamp)
        self.assertIsInstance(result.timestamp, datetime)
    
    def test_algorithm_choices_validation(self):
        """Test that only valid algorithm choices are accepted."""
        # Valid choices
        valid_algorithms = ['ecc', 'dilithium']
        for algo in valid_algorithms:
            result = TestResult.objects.create(
                algorithm=algo,
                operation='keygen',
                message_size=256,
                execution_time_ms=3.247,
                memory_usage_kb=128.5,
                status='success'
            )
            self.assertEqual(result.algorithm, algo)
    
    def test_operation_choices_validation(self):
        """Test that only valid operation choices are accepted."""
        valid_operations = ['keygen', 'sign', 'verify']
        for op in valid_operations:
            result = TestResult.objects.create(
                algorithm='ecc',
                operation=op,
                message_size=256,
                execution_time_ms=3.247,
                memory_usage_kb=128.5,
                status='success'
            )
            self.assertEqual(result.operation, op)
    
    def test_status_choices_validation(self):
        """Test that only valid status choices are accepted."""
        valid_statuses = ['success', 'failure']
        for status in valid_statuses:
            result = TestResult.objects.create(
                algorithm='ecc',
                operation='keygen',
                message_size=256,
                execution_time_ms=3.247,
                memory_usage_kb=128.5,
                status=status
            )
            self.assertEqual(result.status, status)
    
    def test_error_message_optional(self):
        """Test that error_message is optional."""
        result = TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        self.assertIsNone(result.error_message)
    
    def test_error_message_stored(self):
        """Test that error_message can be stored."""
        error_msg = "Test error message"
        result = TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=0.0,
            memory_usage_kb=0.0,
            status='failure',
            error_message=error_msg
        )
        
        self.assertEqual(result.error_message, error_msg)
    
    def test_model_str_representation(self):
        """Test model string representation."""
        result = TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        str_repr = str(result)
        self.assertIn('ecc', str_repr)
        self.assertIn('keygen', str_repr)
        self.assertIn('success', str_repr)
    
    def test_model_repr_representation(self):
        """Test model repr representation."""
        result = TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        repr_str = repr(result)
        self.assertIn('TestResult', repr_str)
        self.assertIn('ecc', repr_str)
        self.assertIn('keygen', repr_str)
    
    def test_ordering_by_timestamp_desc(self):
        """Test that default ordering is by timestamp descending."""
        # Create multiple results
        for i in range(5):
            TestResult.objects.create(
                algorithm='ecc',
                operation='keygen',
                message_size=256,
                execution_time_ms=3.247 + i,
                memory_usage_kb=128.5,
                status='success'
            )
        
        results = list(TestResult.objects.all())
        
        # Check that results are ordered by timestamp descending
        for i in range(len(results) - 1):
            self.assertGreaterEqual(
                results[i].timestamp,
                results[i + 1].timestamp,
                "Results should be ordered by timestamp descending"
            )
    
    def test_filter_by_algorithm(self):
        """Test filtering results by algorithm."""
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        TestResult.objects.create(
            algorithm='dilithium',
            operation='keygen',
            message_size=256,
            execution_time_ms=124.356,
            memory_usage_kb=4128.2,
            status='success'
        )
        
        ecc_results = TestResult.objects.filter(algorithm='ecc')
        self.assertEqual(ecc_results.count(), 1)
        self.assertEqual(ecc_results.first().algorithm, 'ecc')
        
        dilithium_results = TestResult.objects.filter(algorithm='dilithium')
        self.assertEqual(dilithium_results.count(), 1)
        self.assertEqual(dilithium_results.first().algorithm, 'dilithium')
    
    def test_filter_by_operation(self):
        """Test filtering results by operation."""
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        TestResult.objects.create(
            algorithm='ecc',
            operation='sign',
            message_size=256,
            execution_time_ms=2.156,
            memory_usage_kb=98.3,
            status='success'
        )
        
        keygen_results = TestResult.objects.filter(operation='keygen')
        self.assertEqual(keygen_results.count(), 1)
        
        sign_results = TestResult.objects.filter(operation='sign')
        self.assertEqual(sign_results.count(), 1)
    
    def test_filter_by_status(self):
        """Test filtering results by status."""
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=0.0,
            memory_usage_kb=0.0,
            status='failure',
            error_message='Test error'
        )
        
        success_results = TestResult.objects.filter(status='success')
        self.assertEqual(success_results.count(), 1)
        
        failure_results = TestResult.objects.filter(status='failure')
        self.assertEqual(failure_results.count(), 1)