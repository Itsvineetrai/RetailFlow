"""
Custom exceptions for the AeroMart Data Platform.
"""


class AeroMartException(Exception):
    """
    Base exception for the project.
    """

    pass


class ConfigurationError(AeroMartException):
    """
    Raised when configuration is invalid.
    """

    pass


class DataValidationError(AeroMartException):
    """
    Raised when incoming data fails validation.
    """

    pass


class CurrencyConversionError(AeroMartException):
    """
    Raised when exchange-rate conversion fails.
    """

    pass


class KafkaConnectionError(AeroMartException):
    """
    Raised when Kafka is unavailable.
    """

    pass


class StorageError(AeroMartException):
    """
    Raised for MinIO or storage-related failures.
    """

    pass