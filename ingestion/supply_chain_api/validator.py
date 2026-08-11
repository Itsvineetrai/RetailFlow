"""
RetailFlow Supply Chain API Validator.

Validates records received from the external REST API
before they are published to Kafka.
"""

from __future__ import annotations

from typing import Any

from core.exceptions import ValidationError
from core.logger import get_logger

logger = get_logger(__name__)


class SupplyChainAPIValidator:
    """
    Validates Supply Chain API records.
    """

    REQUIRED_FIELDS = {
        "order_id",
        "supplier_id",
        "product_id",
        "quantity",
        "status",
    }

    @classmethod
    def validate_record(
        cls,
        record: dict[str, Any],
    ) -> bool:
        """
        Validate a single Supply Chain API record.

        Returns
        -------
        bool
            True when the record is valid.

        Raises
        ------
        ValidationError
            If required fields are missing or invalid.
        """

        if not isinstance(record, dict):

            raise ValidationError(
                "Supply Chain record must be a JSON object."
            )

        missing_fields = (
            cls.REQUIRED_FIELDS - record.keys()
        )

        if missing_fields:

            raise ValidationError(
                "Missing required Supply Chain fields: "
                f"{sorted(missing_fields)}"
            )

        if not str(record["order_id"]).strip():

            raise ValidationError(
                "order_id cannot be empty."
            )

        if not str(record["supplier_id"]).strip():

            raise ValidationError(
                "supplier_id cannot be empty."
            )

        if not str(record["product_id"]).strip():

            raise ValidationError(
                "product_id cannot be empty."
            )

        try:

            quantity = int(record["quantity"])

        except (TypeError, ValueError) as exc:

            raise ValidationError(
                "quantity must be an integer."
            ) from exc

        if quantity <= 0:

            raise ValidationError(
                "quantity must be greater than zero."
            )

        if not str(record["status"]).strip():

            raise ValidationError(
                "status cannot be empty."
            )

        return True

    @classmethod
    def validate_records(
        cls,
        records: list[dict[str, Any]],
    ) -> tuple[
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        """
        Validate all API records.

        Returns
        -------
        tuple
            (valid_records, invalid_records)
        """

        valid_records: list[dict[str, Any]] = []
        invalid_records: list[dict[str, Any]] = []

        for record in records:

            try:

                cls.validate_record(record)

                valid_records.append(record)

            except ValidationError as exc:

                logger.error(
                    f"Invalid Supply Chain record: {exc}"
                )

                invalid_records.append(
                    {
                        "record": record,
                        "error": str(exc),
                    }
                )

        logger.info(
            "Supply Chain validation complete: "
            f"{len(valid_records)} valid, "
            f"{len(invalid_records)} invalid."
        )

        return valid_records, invalid_records