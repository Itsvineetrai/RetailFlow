# RetailFlow — Scalable Real-Time Retail Data Platform

> **Problem:** Enable real-time retail analytics and demand forecasting from high-volume transaction streams.

RetailFlow is a production-style retail data platform built around **Apache Kafka, Apache Spark Structured Streaming, Delta Lake, Apache Airflow, MinIO/S3, and machine-learning forecasting**. It ingests transaction events, processes them through a Bronze/Silver/Gold data-lake architecture, orchestrates downstream workloads, and exposes analytical and forecasting outputs through a dashboard and analytics-agent layer.

---

## Architecture

```text
E-commerce Producer
        |
        v
+----------------------+
| Apache Kafka         |
| retail.transactions  |
| 6 partitions         |
+----------+-----------+
           |
           v
+------------------------------+
| Spark Structured Streaming   |
| PySpark + JSON Schema        |
+--------------+---------------+
               |
               v
+----------------------+
| Bronze Delta         |
| Raw / immutable      |
+----------+-----------+
           |
           v
+----------------------+
| Silver Delta         |
| Cleaned / validated  |
+----------+-----------+
           |
           v
+----------------------+
| Gold Delta           |
| Analytics / ML data  |
+----------+-----------+
           |
     +-----+------+----------------+
     |            |                |
     v            v                v
 Forecasting   Streamlit      Analytics Agent
     |          Dashboard       Natural Language
     |            |                |
     +------------+----------------+
                  |
                  v
          Retail Insights

Infrastructure / Orchestration:
Docker Compose + Airflow + Spark Cluster + MinIO/S3
```

---

## Data Lake

```text
s3a://retailflow/
├── landing/
├── bronze/
│   └── transactions/
├── silver/
│   ├── transactions/
│   └── forecasting_history/
├── gold/
│   ├── daily_demand/
│   ├── forecasting_dataset/
│   └── transactions/
├── quarantine/
├── archive/
└── checkpoints/
    ├── bronze/
    ├── transactions/
    ├── silver/
    └── gold/
```

| Layer | Purpose |
|---|---|
| Landing | Source/batch data |
| Bronze | Raw streaming ingestion |
| Silver | Cleaned and transformed data |
| Gold | Business and ML-ready datasets |
| Checkpoints | Spark streaming state |
| Quarantine | Invalid records |
| Archive | Historical retention |

---

## Technology Stack

**Languages:** Python, SQL  
**Streaming:** Apache Kafka, Spark Structured Streaming  
**Processing:** Apache Spark, PySpark  
**Storage:** Delta Lake, MinIO/S3  
**Orchestration:** Apache Airflow  
**Infrastructure:** Docker / Docker Compose  
**ML:** scikit-learn  
**Analytics:** Streamlit, Power BI where applicable  
**Monitoring:** Prometheus / Grafana  

---

## Project Structure

```text
RetailFlow/
├── airflow/
│   └── dags/
├── configs/
│   └── spark-defaults.conf
├── core/
│   ├── config.py
│   ├── constants.py
│   ├── kafka_client.py
│   ├── logger.py
│   └── spark_session.py
├── dashboard/
│   ├── app.py
│   ├── config.py
│   └── pages/
├── forecasting/
│   ├── features/
│   ├── serving/
│   └── training/
├── ingestion/
│   └── ecommerce_stream/
├── pipelines/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── scripts/
├── serving/
│   ├── apis/
│   ├── fastapi/
│   └── reporting/
├── spark/
│   └── streaming/
├── storage/
├── docker-compose.yml
├── Dockerfile.airflow
├── requirements.txt
└── README.md
```

---

# Quick Start

## 1. Prerequisites

Development environment:

- Windows 11
- Python 3.11
- Docker Desktop
- Docker Compose
- Java 17
- Git

Verify:

```powershell
python --version
docker --version
docker compose version
java -version
git --version
```

## 2. Clone and setup

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd RetailFlow
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Start infrastructure

```powershell
docker compose up -d
docker compose ps
```

Check scheduler:

```powershell
docker compose logs -f airflow-scheduler
```

---

# Run Order

## Step 1 — Verify Kafka

```powershell
docker compose exec kafka kafka-topics.sh `
  --bootstrap-server kafka:9092 `
  --list
```

Describe the transaction topic:

```powershell
docker compose exec kafka kafka-topics.sh `
  --bootstrap-server kafka:9092 `
  --describe `
  --topic retail.transactions
```

Expected local configuration:

```text
Topic: retail.transactions
PartitionCount: 6
ReplicationFactor: 1
```

---

## Step 2 — Run the transaction producer

Controlled benchmark:

```powershell
.\.venv\Scripts\python.exe -m ingestion.ecommerce_stream.producer --benchmark --count 1000
```

Validated example:

```text
Messages sent: 1,000
Duration: 0.375 seconds
Actual throughput: 2,667.04 msg/sec
```

---

## Step 3 — Start Bronze streaming

Docker/Airflow environment:

```powershell
docker compose exec airflow-scheduler `
  python -m scripts.run_bronze
```

Local environment:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_bronze
```

Expected startup:

```text
Spark Session created successfully.
Starting Bronze Delta Pipeline...
Reading Kafka Stream...
Kafka Stream Connected.
Starting streaming Bronze Delta writer...
Streaming Bronze Delta writer started.
Bronze Delta Streaming Started.
```

Bronze output:

```text
s3a://retailflow/bronze/transactions
```

Checkpoint:

```text
s3a://retailflow/checkpoints/bronze
```

---

## Step 4 — Run Silver

```powershell
docker compose exec airflow-scheduler `
  python -m scripts.run_silver
```

Or:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_silver
```

---

## Step 5 — Run Gold

```powershell
docker compose exec airflow-scheduler `
  python -m scripts.run_gold
```

Or:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_gold
```

Gold datasets include:

```text
gold/daily_demand
gold/forecasting_dataset
gold/transactions
```

---

## Step 6 — Forecasting

The forecasting workflow uses the latest available historical data and generates recursive 7-day forecasts across store-product series.

Recorded evaluation:

| Model | MAE | RMSE | WAPE |
|---|---:|---:|---:|
| Naive | 1.6400 | 3.0919 | 0.4592 |
| Lag 7 | 1.6314 | 2.9204 | 0.4568 |
| Gradient Boosting | **1.3241** | **2.3103** | **0.3708** |

**WAPE improvement vs Lag-7: 18.83%**

Evaluation window:

```text
Training: 2026-02-14 → 2026-08-05
Holdout:  2026-08-06 → 2026-08-12

Training rows: 8,650
Holdout rows: 350
Store-product pairs: 50
Forecast horizon: 7 days
```

---

# Dashboard

Start Streamlit from the repository root:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboardpp.py
```

If the dashboard package cannot be resolved:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m streamlit run dashboardpp.py
```

The dashboard provides analytical views over RetailFlow's Gold and forecasting datasets.

Example areas:

- Executive KPIs
- Sales analytics
- Demand forecasting
- Inventory analytics
- Retail trends

---

# Analytics Agent

The analytics-agent layer sits above the data platform:

```text
User Question
      |
      v
Intent Routing
      |
      +---- Sales Analytics
      |
      +---- Forecast Analytics
      |
      +---- Inventory Analytics
      |
      v
Analytical Tools
      |
      v
Gold / Forecasting Data
      |
      v
Natural-Language Insight
```

The agent is an application layer over governed analytical datasets; it does not replace Kafka, Spark, Delta Lake, or Airflow.

---

# Airflow

Airflow orchestrates the downstream workflows.

```text
Kafka / Source
      |
      v
   Bronze
      |
      v
   Silver
      |
      v
    Gold
      |
   +--+----------------+
   |                   |
   v                   v
Forecasting        Dashboard /
                   Analytics
```

Airflow UI:

```text
http://localhost:8080
```

Scheduler status:

```powershell
docker compose ps airflow-scheduler
```

Scheduler logs:

```powershell
docker compose logs airflow-scheduler --tail 200
```

---

# Spark Cluster

Check the Spark master:

```powershell
docker compose exec spark-master `
  bash -c "curl -s http://localhost:8080/json/"
```

Development cluster used during testing:

```text
Workers: 2
Total cores: 4
Total memory: 4096 MB
```

---

# MinIO / Delta Verification

List buckets:

```powershell
docker compose exec minio mc ls local
```

Inspect Bronze checkpoints:

```powershell
docker compose exec minio `
  mc ls --recursive local/retailflow/checkpoints/bronze
```

Inspect the Bronze Delta transaction log:

```powershell
docker compose exec minio `
  mc ls --recursive local/retailflow/bronze/transactions/_delta_log
```

A valid Delta table contains transaction-log entries such as:

```text
00000000000000000000.json
00000000000000000001.json
...
_last_checkpoint
```

---

# Performance Benchmarks

Measured development-environment results:

| Workload | Target | Measured |
|---|---:|---:|
| 10K batch | — | **5,196 msg/s** |
| 30K | 5,000 msg/s | **239 msg/s** |
| 60K | 10,000 msg/s | **~5,213 msg/s** |

These are **local measured benchmarks**, not production capacity claims.

The 30K workload exposed a throughput bottleneck, while the higher-volume test demonstrated approximately 5.2K msg/s measured throughput.

---

# Key Results

| Metric | Result |
|---|---:|
| Kafka transaction partitions | **6** |
| Verified Kafka messages | **145K+** |
| Verified Bronze records | **180K+** |
| Forecasting series | **50 store-product pairs** |
| Forecast horizon | **7 days** |
| WAPE improvement | **18.83%** |
| Best model | **Gradient Boosting** |
| Best MAE | **1.3241** |
| Best RMSE | **2.3103** |
| Best WAPE | **0.370762** |
| High-volume measured throughput | **~5.2K msg/s** |

---

# Screenshots

Create:

```text
docs/
└── screenshots/
    ├── architecture.png
    ├── kafka-topic.png
    ├── spark-ui.png
    ├── airflow-dag.png
    ├── minio-datalake.png
    ├── dashboard-overview.png
    ├── forecasting.png
    └── monitoring.png
```

Embed them:

### Architecture

![RetailFlow Architecture](docs/screenshots/architecture.png)

### Kafka

![Kafka Topic](docs/screenshots/kafka-topic.png)

### Spark

![Spark UI](docs/screenshots/spark-ui.png)

### Airflow

![Airflow DAG](docs/screenshots/airflow-dag.png)

### Dashboard

![RetailFlow Dashboard](docs/screenshots/dashboard-overview.png)

### Forecasting

![Demand Forecasting](docs/screenshots/forecasting.png)

### Monitoring

![Monitoring](docs/screenshots/monitoring.png)

> Replace these placeholders with real screenshots. Never commit passwords, tokens, API keys, or other secrets.

---

# Monitoring

RetailFlow supports operational observability through:

```text
Spark
  |
  v
Prometheus metrics
  |
  v
Grafana
```

Relevant signals include:

- Streaming query status
- Batch processing
- Executor utilization
- CPU/memory
- Throughput
- Spark application state
- Streaming failures

---

# Engineering Highlights

### Real-Time Data Engineering

- Kafka event ingestion
- 6-partition transaction topic
- Spark Structured Streaming
- Checkpoint-based recovery
- Delta Lake streaming writes

### Data Lake

- Bronze/Silver/Gold medallion architecture
- S3-compatible MinIO object storage
- Delta transaction logs
- Batch + streaming workflows
- Quarantine and archive paths

### Orchestration

- Apache Airflow
- Spark application orchestration
- Repeatable downstream processing
- Forecasting workflow integration

### Machine Learning

- Temporal/lag features
- Gradient Boosting forecasting
- Holdout evaluation
- MAE / RMSE / WAPE
- Recursive 7-day forecasting
- 50 store-product series

### Analytics

- Streamlit dashboard
- Gold-layer analytical datasets
- Forecasting analytics
- Natural-language analytics-agent foundation

---

# Known Limitations

RetailFlow is a development/capstone implementation rather than a production deployment.

- Benchmarks were performed on the local Docker/Spark environment.
- Measured throughput was approximately 5.2K msg/s in the validated high-volume workload.
- The local Kafka environment uses replication factor 1.
- Production deployment would require stronger fault tolerance, security, secret management, governance, and multi-node capacity testing.
- Dashboard and analytics-agent capabilities depend on the currently implemented datasets and tools.

These limitations are documented intentionally rather than presenting local test results as production guarantees.

---

# Future Improvements

1. Optimize Kafka/Spark throughput bottlenecks.
2. Expand automated data-quality monitoring.
3. Improve dynamic forecasting feature generation.
4. Add model drift and forecast-performance monitoring.
5. Expand analytics-agent tools.
6. Add role-based dashboard access.
7. Add schema/data-contract validation.
8. Add CI/CD and integration testing.
9. Perform multi-node/cloud capacity testing.
10. Strengthen Kafka replication and failure-recovery testing.

---

# Verification Checklist

- [ ] Docker services healthy
- [ ] Kafka reachable from Spark/Airflow
- [ ] `retail.transactions` exists
- [ ] Kafka partitions have leaders
- [ ] Producer publishes events
- [ ] Spark Kafka connector loads
- [ ] Bronze streaming query starts
- [ ] Bronze Delta log exists
- [ ] Bronze checkpoint exists
- [ ] Silver completes
- [ ] Gold completes
- [ ] Forecasting evaluation completes
- [ ] Airflow workflows execute
- [ ] Streamlit dashboard starts
- [ ] Dashboard reads Gold/forecasting data
- [ ] Monitoring is available
- [ ] No secrets are committed

---

# Git Commands

```powershell
git status
git diff
git add .
git commit -m "docs: add comprehensive RetailFlow README"
git push
```

---

## License

See the repository `LICENSE` file.
