"""Django Views for Cryptographic Testing Application"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import csv
from datetime import datetime

from .controller import TestController
from .models import TestResult

# Global controller instance
controller = TestController()


def index(request):
    """Render main interface page."""
    return render(request, 'index.html')


@require_http_methods(["POST"])
def run_test(request):
    """Execute cryptographic test and return results."""
    try:
        data = json.loads(request.body)
        algorithm = data.get('algorithm')
        operation = data.get('operation')
        message_size = int(data.get('message_size', 256))

        # Validate inputs
        if algorithm not in ['ecc', 'dilithium']:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid algorithm: {algorithm}'
            }, status=400)

        if operation not in ['keygen', 'sign', 'verify']:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid operation: {operation}'
            }, status=400)

        if not (32 <= message_size <= 4096):
            return JsonResponse({
                'status': 'error',
                'message': f'Message size must be between 32 and 4096 bytes'
            }, status=400)

        # Run test
        result = controller.run_test(algorithm, operation, message_size)

        # Save to database
        test_result = TestResult.objects.create(
            algorithm=algorithm,
            operation=operation,
            message_size=message_size,
            execution_time_ms=result.execution_time_ms,
            memory_usage_kb=result.memory_usage_kb,
            status=result.status,
            error_message=result.error_message
        )

        return JsonResponse({
            'status': 'success',
            'data': {
                'id': test_result.id,
                'timestamp': result.timestamp,
                'algorithm': result.algorithm,
                'operation': result.operation,
                'message_size': result.message_size,
                'execution_time_ms': round(result.execution_time_ms, 3),
                'memory_usage_kb': round(result.memory_usage_kb, 2),
                'status': result.status
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_results(request):
    """Get all test results."""
    try:
        results = TestResult.objects.values(
            'id', 'timestamp', 'algorithm', 'operation',
            'message_size', 'execution_time_ms', 'memory_usage_kb', 'status'
        ).order_by('-timestamp')

        return JsonResponse({
            'status': 'success',
            'count': len(list(results)),
            'data': list(results)
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def export_csv(request):
    """Export all results to CSV file."""
    try:
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crypto_results.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'timestamp', 'algorithm', 'operation', 'message_size',
            'execution_time_ms', 'memory_usage_kb', 'status'
        ])

        for result in TestResult.objects.all().values_list(
                'timestamp', 'algorithm', 'operation', 'message_size',
                'execution_time_ms', 'memory_usage_kb', 'status'
        ):
            writer.writerow(result)

        return response

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_statistics(request):
    """Get performance statistics."""
    try:
        from django.db.models import Avg, Min, Max, Count

        stats = {}

        for algo in ['ecc', 'dilithium']:
            algo_data = TestResult.objects.filter(
                algorithm=algo,
                status='success'
            ).values('operation').annotate(
                count=Count('id'),
                avg_time=Avg('execution_time_ms'),
                min_time=Min('execution_time_ms'),
                max_time=Max('execution_time_ms'),
                avg_memory=Avg('memory_usage_kb')
            )

            stats[algo] = list(algo_data)

        return JsonResponse({
            'status': 'success',
            'data': stats
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
