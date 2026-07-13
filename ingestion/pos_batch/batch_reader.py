"""
RetailFlow POS Batch Reader

Reads POS batch files from the Landing Zone with Windows path compatibility.

Supported formats:
    - CSV
    - Parquet (Future)
    - XML (Future)

Author: RetailFlow
"""

from __future__ import annotations

from pathlib import Path
from pyspark.sql import DataFrame

from core.logger import get_logger
from core.spark_session import SparkSessionManager
from core.exceptions import ValidationError

logger = get_logger(__name__)


class POSBatchReader:
    """
    Reads batch POS files using Spark.
    """

    SUPPORTED_EXTENSIONS = {".csv"}

    def __init__(self, app_name: str = "RetailFlow-POS-Reader") -> None:
        self.spark = SparkSessionManager.get_session(app_name)

    def read_csv(
        self,
        file_path: str | Path,
        header: bool = True,
        infer_schema: bool = True,
    ) -> DataFrame:
        """
        Read a CSV file.

        Parameters
        ----------
        file_path : str | Path
            Path to CSV file.
        header : bool
            Whether file contains header.
        infer_schema : bool
            Whether Spark should infer schema.

        Returns
        -------
        DataFrame
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file type: {file_path.suffix}"
            )

        logger.info(f"Reading POS batch file: {file_path}")

        # FIX: Convert Windows paths to uniform URI standard format (file:///C:/...)
        # This prevents the Java/Py4J layer from misinterpreting backslashes as escape characters.
        spark_compatible_path = file_path.as_uri()

        try:
            df = (
                self.spark.read
                .option("header", "true" if header else "false")
                .option("inferSchema", "true" if infer_schema else "false")
                .csv(spark_compatible_path)
            )

            # Performance Pro-Tip: Cache count so it doesn't calculate twice during log and return
            record_count = df.count()
            logger.success(
                f"Successfully loaded {record_count} records."
            )
            return df

        except Exception as e:
            logger.error(f"Failed to read CSV into Spark DataFrame: {str(e)}")
            raise

    @staticmethod
    def preview(
        dataframe: DataFrame,
        rows: int = 10,
    ) -> None:
        """
        Display sample records.
        """
        dataframe.show(rows, truncate=False)

    @staticmethod
    def print_schema(
        dataframe: DataFrame,
    ) -> None:
        """
        Display Spark schema.
        """
        dataframe.printSchema()

    @staticmethod
    def row_count(
        dataframe: DataFrame,
    ) -> int:
        """
        Returns DataFrame row count.
        """
        return dataframe.count()
