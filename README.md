# RetailFlow

Enterprise Retail Analytics Platform

---

## Overview

RetailFlow is a production-grade retail data platform capable of processing:

- POS batch transactions
- Real-time e-commerce events
- Supply chain API data

The platform supports:

- Streaming analytics
- Batch processing
- Financial reconciliation
- Inventory management
- Demand forecasting

---

## Technology Stack

- Python 3.11
- Apache Kafka
- Apache Spark 3.5.x
- Delta Lake
- Apache Airflow
- MinIO
- PostgreSQL
- Docker Compose
- Prometheus
- Grafana

---

## Architecture

POS Batch
↓

Kafka

↓

Spark Structured Streaming

↓

Bronze

↓

Silver

↓

Gold

↓

Dashboards / APIs / ML

---

## Medallion Layers

Bronze

- Raw immutable data

Silver

- Cleaned and validated

Gold

- Business-ready datasets

---

## Features

- Multi-source ingestion
- Near real-time inventory
- Batch reconciliation
- Financial-grade precision
- Multi-currency support
- Country-aware processing
- Auto-scalable Spark architecture
- Monitoring
- Data Quality
- Airflow orchestration

---

## Project Structure

configs/

core/

ingestion/

kafka/

spark/

pipelines/

financial_engine/

inventory/

forecasting/

serving/

airflow/

monitoring/

storage/

tests/

docs/

---

## Start

```powershell
docker compose up -d
```

---

## Stop

```powershell
docker compose down
```

---

## License

MIT