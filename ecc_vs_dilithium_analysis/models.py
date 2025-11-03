"""Django Models for Cryptographic Test Results"""
from django.db import models


class TestResult(models.Model):
    """Model storing cryptographic test results."""

    ALGORITHM_CHOICES = [
        ('ecc', 'ECC (Elliptic Curve)'),
        ('dilithium', 'CRYSTALS-Dilithium'),
    ]

    OPERATION_CHOICES = [
        ('keygen', 'Key Generation'),
        ('sign', 'Signature Generation'),
        ('verify', 'Signature Verification'),
    ]

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]

    # Fields
    timestamp = models.DateTimeField(auto_now_add=True)
    algorithm = models.CharField(max_length=20, choices=ALGORITHM_CHOICES)
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    message_size = models.IntegerField()
    execution_time_ms = models.FloatField()
    memory_usage_kb = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'crypto_test_result'
        verbose_name = 'Test Result'
        verbose_name_plural = 'Test Results'
        indexes = [
            models.Index(fields=['algorithm', 'operation']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.algorithm} - {self.operation} - {self.status}"

    def __repr__(self):
        return f"<TestResult: {self.algorithm} {self.operation} {self.execution_time_ms}ms>"
