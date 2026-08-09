from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame

from core.exceptions import ValidationError
from core.logger import get_logger
from core.spark_session import SparkSessionManager

logger = get_logger(__name__)


class POSBatchReader:
    """
    Reads POS batch files using Spark.

    Supported formats:
        - CSV
        - JSON
        - Parquet

    Supported locations:
        - Local filesystem paths
        - file:// URIs
        - s3a:// URIs
    """

    SUPPORTED_EXTENSIONS = {
        ".csv",
        ".json",
        ".parquet",
    }

    def __init__(
        self,
        app_name: str = "RetailFlow-POS-Batch",
    ) -> None:
        self.spark = SparkSessionManager.get_session(app_name)

    @classmethod
    def _is_remote_path(cls, file_path: str) -> bool:
        """
        Determine whether the supplied path is a Spark filesystem URI.
        """

        return file_path.startswith(
            (
                "s3a://",
                "s3://",
                "file://",
            )
        )

    @classmethod
    def _validate_local_file(
        cls,
        file_path: str | Path,
    ) -> Path:
        """
        Validate a local filesystem path.
        """

        path = Path(file_path).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"POS batch file does not exist: {path}"
            )

        if not path.is_file():
            raise ValidationError(
                f"POS batch path is not a file: {path}"
            )

        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported POS batch file type: "
                f"{path.suffix}. "
                f"Supported types: "
                f"{sorted(cls.SUPPORTED_EXTENSIONS)}"
            )

        return path

    @classmethod
    def _validate_remote_path(
        cls,
        file_path: str,
    ) -> str:
        """
        Validate a Spark filesystem URI.

        Spark itself will perform the actual existence check when
        the DataFrame is evaluated.
        """

        if not cls._is_remote_path(file_path):
            raise ValidationError(
                f"Unsupported remote path: {file_path}"
            )

        # Extract extension from the URI without converting it
        # into a Windows Path.
        path_without_query = file_path.split("?", 1)[0]
        extension = Path(path_without_query).suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported POS batch file type: "
                f"{extension}. "
                f"Supported types: "
                f"{sorted(cls.SUPPORTED_EXTENSIONS)}"
            )

        return file_path

    @classmethod
    def _prepare_path(
        cls,
        file_path: str | Path,
    ) -> tuple[str, str]:
        """
        Prepare an input path for Spark.

        Returns
        -------
        tuple[str, str]
            Spark-compatible path and file extension.
        """

        raw_path = str(file_path)

        # --------------------------------------------------------------
        # Remote Spark filesystem
        # --------------------------------------------------------------

        if cls._is_remote_path(raw_path):

            spark_path = cls._validate_remote_path(
                raw_path
            )

            extension = Path(
                raw_path.split("?", 1)[0]
            ).suffix.lower()

            return spark_path, extension

        # --------------------------------------------------------------
        # Local filesystem
        # --------------------------------------------------------------

        path = cls._validate_local_file(
            file_path
        )

        return path.as_uri(), path.suffix.lower()

    def read_csv(
        self,
        file_path: str | Path,
        header: bool = True,
        infer_schema: bool = True,
    ) -> DataFrame:
        """
        Read a CSV POS batch file.
        """

        spark_path, extension = self._prepare_path(
            file_path
        )

        if extension != ".csv":
            raise ValidationError(
                f"Expected CSV file, received: {extension}"
            )

        logger.info(
            f"Reading POS CSV: {spark_path}"
        )

        try:
            dataframe = (
                self.spark.read
                .option(
                    "header",
                    str(header).lower(),
                )
                .option(
                    "inferSchema",
                    str(infer_schema).lower(),
                )
                .csv(spark_path)
            )

            logger.success(
                "POS CSV loaded successfully."
            )

            return dataframe

        except Exception:
            logger.exception(
                f"Failed to read POS CSV: {spark_path}"
            )
            raise

    def read_json(
        self,
        file_path: str | Path,
        multiline: bool = False,
    ) -> DataFrame:
        """
        Read a JSON POS batch file.
        """

        spark_path, extension = self._prepare_path(
            file_path
        )

        if extension != ".json":
            raise ValidationError(
                f"Expected JSON file, received: {extension}"
            )

        logger.info(
            f"Reading POS JSON: {spark_path}"
        )

        try:
            dataframe = (
                self.spark.read
                .option(
                    "multiLine",
                    str(multiline).lower(),
                )
                .json(spark_path)
            )

            logger.success(
                "POS JSON loaded successfully."
            )

            return dataframe

        except Exception:
            logger.exception(
                f"Failed to read POS JSON: {spark_path}"
            )
            raise

    def read_parquet(
        self,
        file_path: str | Path,
    ) -> DataFrame:
        """
        Read a Parquet POS batch file.
        """

        spark_path, extension = self._prepare_path(
            file_path
        )

        if extension != ".parquet":
            raise ValidationError(
                f"Expected Parquet file, received: {extension}"
            )

        logger.info(
            f"Reading POS Parquet: {spark_path}"
        )

        try:
            dataframe = self.spark.read.parquet(
                spark_path
            )

            logger.success(
                "POS Parquet loaded successfully."
            )

            return dataframe

        except Exception:
            logger.exception(
                f"Failed to read POS Parquet: {spark_path}"
            )
            raise

    def read(
        self,
        file_path: str | Path,
    ) -> DataFrame:
        """
        Automatically select the appropriate reader.
        """

        raw_path = str(file_path)

        if self._is_remote_path(raw_path):

            extension = Path(
                raw_path.split("?", 1)[0]
            ).suffix.lower()

        else:

            extension = Path(
                raw_path
            ).suffix.lower()

        if extension == ".csv":
            return self.read_csv(file_path)

        if extension == ".json":
            return self.read_json(file_path)

        if extension == ".parquet":
            return self.read_parquet(file_path)

        raise ValidationError(
            f"Unsupported POS batch file type: "
            f"{extension}. "
            f"Supported types: "
            f"{sorted(self.SUPPORTED_EXTENSIONS)}"
        )

    @staticmethod
    def preview(
        dataframe: DataFrame,
        rows: int = 10,
    ) -> None:
        """
        Display sample records.
        """

        dataframe.show(
            rows,
            truncate=False,
        )

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
        Return DataFrame row count.
        """

        return dataframe.count()