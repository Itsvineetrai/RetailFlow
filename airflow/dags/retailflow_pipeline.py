"""
RetailFlow Data Platform DAG

Current Workflow

Bronze (Streaming - External Service)
        ↓
Silver Pipeline
        ↓
Gold Pipeline

Future

Gold Pipeline
        ↓
Feature Store
        ↓
Forecasting
        ↓
Dashboard
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "retailflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(

    dag_id="retailflow_pipeline",

    description="RetailFlow Delta Medallion Pipeline",

    default_args=default_args,

    start_date=datetime(2026, 1, 1),

    schedule="@hourly",

    catchup=False,

    max_active_runs=1,

    tags=[
        "retailflow",
        "delta",
        "spark",
        "etl",
    ],

) as dag:

    silver_pipeline = BashOperator(

        task_id="silver_pipeline",

        bash_command="""
        set -e
        cd /opt/airflow/project
        python -m scripts.run_silver
        """,
    )

    gold_pipeline = BashOperator(

        task_id="gold_pipeline",

        bash_command="""
        set -e
        cd /opt/airflow/project
        python -m scripts.run_gold
        """,

    )
    demand_forecast = BashOperator(

        task_id="demand_forecast",

        bash_command="""
        set -e
        cd /opt/airflow/project
        python -m scripts.run_demand_forecast
        """,
    )

    silver_pipeline >> gold_pipeline >> demand_forecast