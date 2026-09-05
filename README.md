# Hiv Dadr Cardiovascular Risk

> **Domain:** Infectious Disease Surveillance & Microbiology
> **Reference Guidelines & Standards:** `CLSI M100, EUCAST & CDC NHSN Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

D:A:D 5-Year Cardiovascular Risk Equation for HIV
Calculates 5-year CVD risk tailored for people living with HIV on antiretroviral therapy (ART).

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Install Dependencies
```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/hiv-dadr-cardiovascular-risk.git
cd hiv-dadr-cardiovascular-risk

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -e ".[dev]"
```

### Optional: Set Audit Secret Key
```bash
# Linux/macOS
export AUDIT_SECRET_KEY="your-secure-random-key-here"

# Windows
set AUDIT_SECRET_KEY=your-secure-random-key-here
```

---

## ⚙️ Key Capabilities & Algorithmic Modules

### Core Functions

- **`calculate_metrics(**kwargs)`**: Core domain algorithm that computes risk scores from input parameters.
- **`process_single(args)`**: Evaluates a single case and outputs JSON results.
- **`process_batch(input_csv, output_csv)`**: Processes CSV files with patient data and appends risk scores.
- **`main()`**: CLI entry point with subcommands for single/batch processing.

---

## 💻 Usage

### 1. Single Case Evaluation
```bash
# Using dad_hiv_risk module
python dad_hiv_risk.py single --v1 14.5 --v2 4.2 --v3 1.8

# Using the enterprise CLI
python cli.py audit --task-id TASK-001 --target PATIENT-01 --primary 14.5 --secondary 4.2
```

### 2. Batch CSV Processing
```bash
# Using dad_hiv_risk module
python dad_hiv_risk.py batch -i sample.csv -o results.csv

# Using the enterprise CLI
python cli.py batch -i sample.csv -o results.csv
```

### Input CSV Format
```csv
Patient_ID,v1,v2,v3
PT-101,14.5,4.2,1.8
PT-102,8.0,2.1,0.5
```

### 3. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 4. Verify Audit Trail
```bash
python cli.py verify-audit
```

---

## 🛡️ Security Features

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Secure Key Management:** Audit signing key sourced from `AUDIT_SECRET_KEY` environment variable with secure ephemeral fallback.

---

## 🧪 Testing

### Run All Tests
```bash
pytest -v
```

### Run Specific Test Files
```bash
pytest test_dad_hiv_risk.py -v
pytest tests/test_hiv_dadr_cardiovascular_risk.py -v
pytest tests/test_enrichment.py -v
```

### Run Simulation Benchmark
```bash
python simulator.py 1000
```

---

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t hiv-dadr-cardiovascular-risk .

# Run with environment variables
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key hiv-dadr-cardiovascular-risk
```

### Using Docker Compose
```bash
# Set your audit key in docker-compose.yml first
docker compose up -d
```

---

## 📁 Project Structure

```
hiv-dadr-cardiovascular-risk/
├── agents/                  # Enterprise agent framework
│   ├── __init__.py         # Package initialization
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # Security guards, audit trail
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics exporter
│   ├── models.py           # Pydantic data models
│   ├── streamer.py         # WebSocket telemetry
│   ├── supervisor.py       # Multi-agent orchestrator
│   └── workers.py          # Specialized domain workers
├── tests/                  # Test suite
│   ├── test_enrichment.py
│   └── test_hiv_dadr_cardiovascular_risk.py
├── web/                    # Web dashboard
│   └── index.html
├── cli.py                  # Enterprise CLI entry point
├── dad_hiv_risk.py         # Core risk calculation module
├── enrichment.py           # Enrichment feature engines
├── simulator.py            # Load testing simulator
├── sample.csv              # Sample patient data
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container build config
├── docker-compose.yml      # Multi-container orchestration
└── openapi_spec.json       # OpenAPI specification
```

---

## 📐 Risk Classification

| Score Range | Classification | Clinical Recommendation |
|:------------|:---------------|:------------------------|
| < 10.0 | Low / Standard | Standard monitoring |
| 10.0 - 24.9 | Moderate / Intermediate | Close observation |
| >= 25.0 | High / Severe | Urgent clinical intervention |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
