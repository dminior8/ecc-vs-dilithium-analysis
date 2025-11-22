"""
Unit tests for Django views/API endpoints.

Tests validate:
- API endpoint responses
- Request validation
- Error handling
- Data persistence
- JSON response format
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from ecc_vs_dilithium_analysis.models import TestResult
from ecc_vs_dilithium_analysis.controller import ECC_AVAILABLE, DILITHIUM_AVAILABLE


class TestViews(TestCase):
    """Unit tests for views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_index_view(self):
        """Test index page view."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html', status_code=200)
    
    def test_run_test_endpoint_valid_request(self):
        """Test run_test endpoint with valid request."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        data = {
            'algorithm': 'ecc',
            'operation': 'keygen',
            'message_size': 256
        }
        
        response = self.client.post(
            '/api/run_test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('data', response_data)
        self.assertEqual(response_data['data']['algorithm'], 'ecc')
        self.assertEqual(response_data['data']['operation'], 'keygen')
    
    def test_run_test_saves_to_database(self):
        """Test that run_test saves result to database."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        initial_count = TestResult.objects.count()
        
        data = {
            'algorithm': 'ecc',
            'operation': 'keygen',
            'message_size': 256
        }
        
        response = self.client.post(
            '/api/run_test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestResult.objects.count(), initial_count + 1)
        
        saved_result = TestResult.objects.latest('timestamp')
        self.assertEqual(saved_result.algorithm, 'ecc')
        self.assertEqual(saved_result.operation, 'keygen')
    
    def test_run_test_invalid_algorithm(self):
        """Test run_test with invalid algorithm."""
        data = {
            'algorithm': 'invalid',
            'operation': 'keygen',
            'message_size': 256
        }
        
        response = self.client.post(
            '/api/run_test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('Invalid algorithm', response_data['message'])
    
    def test_run_test_invalid_operation(self):
        """Test run_test with invalid operation."""
        data = {
            'algorithm': 'ecc',
            'operation': 'invalid',
            'message_size': 256
        }
        
        response = self.client.post(
            '/api/run_test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
    
    def test_run_test_invalid_message_size_too_small(self):
        """Test run_test with message size too small."""
        data = {
            'algorithm': 'ecc',
            'operation': 'keygen',
            'message_size': 10
        }
        
        response = self.client.post(
            '/api/run_test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
    
    def test_run_test_invalid_message_size_too_large(self):
        """Test run_test with message size too large."""
        data = {
            'algorithm': 'ecc',
            'operation': 'keygen',
            'message_size': 10000
        }
        
        response = self.client.post(
            '/api/run_test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
    
    def test_run_test_invalid_json(self):
        """Test run_test with invalid JSON."""
        response = self.client.post(
            '/api/run_test/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
    
    def test_get_results_endpoint_empty(self):
        """Test get_results endpoint with no results."""
        response = self.client.get('/api/get_results/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['count'], 0)
        self.assertEqual(len(response_data['data']), 0)
    
    def test_get_results_endpoint_with_data(self):
        """Test get_results endpoint with existing data."""
        # Create test data
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        response = self.client.get('/api/get_results/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['count'], 1)
        self.assertEqual(len(response_data['data']), 1)
        self.assertEqual(response_data['data'][0]['algorithm'], 'ecc')
    
    def test_get_results_ordering(self):
        """Test that get_results returns results in correct order."""
        # Create multiple results
        for i in range(3):
            TestResult.objects.create(
                algorithm='ecc',
                operation='keygen',
                message_size=256,
                execution_time_ms=3.247 + i,
                memory_usage_kb=128.5,
                status='success'
            )
        
        response = self.client.get('/api/get_results/')
        response_data = json.loads(response.content)
        
        # Results should be ordered by timestamp descending
        timestamps = [r['timestamp'] for r in response_data['data']]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
    
    def test_export_csv_endpoint(self):
        """Test export_csv endpoint."""
        # Create test data
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.247,
            memory_usage_kb=128.5,
            status='success'
        )
        
        response = self.client.get('/api/export_csv/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('crypto_results.csv', response['Content-Disposition'])
        
        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('timestamp', content)
        self.assertIn('algorithm', content)
        self.assertIn('ecc', content)
    
    def test_get_statistics_endpoint(self):
        """Test get_statistics endpoint."""
        # Create test data for both algorithms
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.0,
            memory_usage_kb=128.0,
            status='success'
        )
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=5.0,
            memory_usage_kb=130.0,
            status='success'
        )
        
        response = self.client.get('/api/statistics/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('data', response_data)
        self.assertIn('ecc', response_data['data'])
    
    def test_get_statistics_only_success(self):
        """Test that statistics only include successful results."""
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=3.0,
            memory_usage_kb=128.0,
            status='success'
        )
        TestResult.objects.create(
            algorithm='ecc',
            operation='keygen',
            message_size=256,
            execution_time_ms=0.0,
            memory_usage_kb=0.0,
            status='failure'
        )
        
        response = self.client.get('/api/statistics/')
        response_data = json.loads(response.content)
        
        # Should only count success
        ecc_stats = response_data['data'].get('ecc', [])
        for stat in ecc_stats:
            self.assertEqual(stat['count'], 1)  # Only success counted