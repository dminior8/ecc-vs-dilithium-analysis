"""
Integration tests for the complete application flow.

Tests validate:
- Full request-response cycle
- Database persistence
- Multiple operations in sequence
- Cross-component interactions
"""

import json
from django.test import TestCase, Client
from ecc_vs_dilithium_analysis.models import TestResult
from ecc_vs_dilithium_analysis.controller import ECC_AVAILABLE, DILITHIUM_AVAILABLE


class TestIntegration(TestCase):
    """Integration tests for complete application flow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_full_workflow_ecc(self):
        """Test complete workflow for ECC: API call -> Database -> Results retrieval."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        # Step 1: Run test via API
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
        result_id = response_data['data']['id']
        
        # Step 2: Verify data was saved to database
        saved_result = TestResult.objects.get(id=result_id)
        self.assertEqual(saved_result.algorithm, 'ecc')
        self.assertEqual(saved_result.operation, 'keygen')
        self.assertEqual(saved_result.status, 'success')
        
        # Step 3: Retrieve results via API
        get_response = self.client.get('/api/get_results/')
        get_data = json.loads(get_response.content)
        
        self.assertEqual(get_response.status_code, 200)
        self.assertGreater(get_data['count'], 0)
        
        # Find our result in the list
        found = False
        for result in get_data['data']:
            if result['id'] == result_id:
                found = True
                self.assertEqual(result['algorithm'], 'ecc')
                break
        
        self.assertTrue(found, "Result should be in get_results response")
    
    def test_multiple_operations_sequence(self):
        """Test multiple operations in sequence."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        operations = ['keygen', 'sign', 'verify']
        results = []
        
        for operation in operations:
            data = {
                'algorithm': 'ecc',
                'operation': operation,
                'message_size': 256
            }
            
            response = self.client.post(
                '/api/run_test/',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.content)
            results.append(response_data['data'])
        
        # Verify all results were saved
        self.assertEqual(TestResult.objects.count(), len(operations))
        
        # Verify all operations are present
        saved_operations = set(
            TestResult.objects.values_list('operation', flat=True)
        )
        self.assertEqual(saved_operations, set(operations))
    
    def test_both_algorithms_comparison(self):
        """Test running tests for both algorithms and comparing results."""
        results = {}
        
        for algorithm in ['ecc', 'dilithium']:
            if algorithm == 'ecc' and not ECC_AVAILABLE:
                continue
            if algorithm == 'dilithium' and not DILITHIUM_AVAILABLE:
                continue
            
            data = {
                'algorithm': algorithm,
                'operation': 'keygen',
                'message_size': 256
            }
            
            response = self.client.post(
                '/api/run_test/',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                results[algorithm] = response_data['data']
        
        # Verify results exist
        self.assertGreater(len(results), 0, "At least one algorithm should work")
        
        # Verify statistics include both
        stats_response = self.client.get('/api/statistics/')
        stats_data = json.loads(stats_response.content)
        
        for algorithm in results.keys():
            self.assertIn(algorithm, stats_data['data'])
    
    def test_csv_export_includes_all_data(self):
        """Test that CSV export includes all test results."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        # Create multiple test results
        for i in range(3):
            data = {
                'algorithm': 'ecc',
                'operation': 'keygen',
                'message_size': 256 + i * 100
            }
            
            self.client.post(
                '/api/run_test/',
                data=json.dumps(data),
                content_type='application/json'
            )
        
        # Export CSV
        response = self.client.get('/api/export_csv/')
        content = response.content.decode('utf-8')
        
        # Count lines (header + 3 data rows)
        lines = content.strip().split('\n')
        self.assertGreaterEqual(len(lines), 4, "CSV should contain header and data rows")
        
        # Verify all results are in CSV
        for i in range(3):
            self.assertIn(str(256 + i * 100), content)
    
    def test_error_handling_preserves_database_state(self):
        """Test that errors don't corrupt database state."""
        initial_count = TestResult.objects.count()
        
        # Try invalid request
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
        
        # Database should not have new entries for invalid requests
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TestResult.objects.count(), initial_count)
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        if not ECC_AVAILABLE:
            self.skipTest("ECC not available")
        
        initial_count = TestResult.objects.count()
        
        # Simulate multiple requests
        for i in range(5):
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
        
        # All should be saved
        self.assertEqual(TestResult.objects.count(), initial_count + 5)