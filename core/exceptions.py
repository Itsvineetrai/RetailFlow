"""
RetailFlow Custom Exceptions

Centralized exception definitions for the RetailFlow platform.

Every module should raise these exceptions instead of generic Exception
where appropriate.
"""

from __future__ import annotations


class RetailFlowException(Exception):
    """
    Base exception for the entire project.
    """

    def __init__(self, message: str = "RetailFlow Exception") -> None:
        super().__init__(message)


# ==============================================================================
# Configuration
# ==============================================================================

class ConfigurationError(RetailFlowException):
    """Raised when application configuration is invalid."""


# ==============================================================================
# Kafka
# ==============================================================================

class KafkaConnectionError(RetailFlowException):
    """Raised when Kafka cannot be reached."""


class KafkaProducerError(RetailFlowException):
    """Raised when producing a Kafka message fails."""


class KafkaConsumerError(RetailFlowException):
    """Raised when consuming Kafka messages fails."""


# ==============================================================================
# Spark
# ==============================================================================

class SparkSessionError(RetailFlowException):
    """Raised when SparkSession creation fails."""


class SparkJobError(RetailFlowException):
    """Raised when a Spark job fails."""


# ==============================================================================
# MinIO
# ==============================================================================

class MinIOConnectionError(RetailFlowException):
    """Raised when MinIO cannot be reached."""


class BucketNotFoundError(RetailFlowException):
    """Raised when the required bucket does not exist."""


class ObjectUploadError(RetailFlowException):
    """Raised when uploading an object fails."""


class ObjectDownloadError(RetailFlowException):
    """Raised when downloading an object fails."""


# ==============================================================================
# Data Validation
# ==============================================================================

class ValidationError(RetailFlowException):
    """Raised when data validation fails."""


class SchemaValidationError(ValidationError):
    """Raised when schema validation fails."""


class InvalidRecordError(ValidationError):
    """Raised when a record is invalid."""


# ==============================================================================
# Storage
# ==============================================================================

class StorageError(RetailFlowException):
    """Raised for storage-related failures."""


# ==============================================================================
# Pipeline
# ==============================================================================

class PipelineError(RetailFlowException):
    """Raised when a pipeline execution fails."""


class ReconciliationError(PipelineError):
    """Raised when batch/stream reconciliation fails."""


# ==============================================================================
# Financial
# ==============================================================================

class CurrencyConversionError(RetailFlowException):
    """Raised when currency conversion fails."""


class TaxCalculationError(RetailFlowException):
    """Raised when tax calculation fails."""


# ==============================================================================
# API
# ==============================================================================

class APIError(RetailFlowException):
    """Raised for API-related failures."""


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class AuthorizationError(APIError):
    """Raised when authorization fails."""


# ==============================================================================
# Unknown
# ==============================================================================

class UnexpectedApplicationError(RetailFlowException):
    """Raised for unexpected application errors.""" 