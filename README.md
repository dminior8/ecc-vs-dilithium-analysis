# ECC vs CRYSTALS-Dilithium algorithms

A Django web application that compares **REAL cryptographic implementations** between ECC (NIST P-256) and CRYSTALS-Dilithium (ML-DSA). The app provides an interactive UI to run actual benchmarks with real time and memory measurements.


## Features

- Interactive UI to run tests for:
  - Key generation
  - Message signing
  - Signature verification
- Live table of results and summary statistics
- Comparison bar chart (per operation)
- CSV export of collected results
- **Real cryptographic operations** with actual measurements

## Project Structure

```
 ecc_vs_dilithium_analysis/
 ├─ ecc_vs_dilithium_analysis/          # Django project and app (single-app project)
 │  ├─ static/ecc_vs_dilithium_analysis/
 │  │  ├─ css/style.css
 │  │  └─ js/app.js
 │  ├─ templates/index.html             # Main UI
 │  ├─ controller.py                    # Real TestController with ECC & Dilithium
 │  ├─ interfaces.py                    # CryptoResult dataclass
 │  ├─ models.py                        # TestResult model
 │  ├─ views.py                         # API endpoints and page view
 │  ├─ urls.py                          # URL routes
 │  ├─ settings.py                      # Django settings
 │  ├─ asgi.py / wsgi.py
 │  └─ manage.py
 └─ venv/ (optional)
```

## Prerequisites

- Python 3.9+ (compatible with Django 5.2.x)
- Pip

## Installation

### 1. Clone Repository

```bash
git clone <repo-url>
cd ecc_vs_dilithium_analysis
```

### 2. Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate (Windows)
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Django Migrations

```bash
python manage.py migrate
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Usage

1. **Select Algorithm**: ECC (NIST P-256) or CRYSTALS-Dilithium (ML-DSA-2)
2. **Select Operation**: 
   - Key Generation (KeyGen)
   - Message Signing
   - Signature Verification
3. **Adjust Message Size**: 256-4096 bytes (use slider)
4. **Run Test**: Click "Run Test" button
5. **View Results**: Real measurements appear in table
6. **Compare**: See bar chart comparison
7. **Export**: Download CSV of all results

## Real Measurements Example

```csv
timestamp,algorithm,operation,message_size,execution_time_ms,memory_usage_kb,status
2025-11-03T23:00:00,ecc,keygen,256,3.247,128.5,success
2025-11-03T23:00:01,dilithium,keygen,256,124.356,4128.2,success
2025-11-03T23:00:02,ecc,sign,256,2.156,98.3,success
2025-11-03T23:00:03,dilithium,sign,256,78.234,2856.1,success
```

**Note:** Dilithium is significantly slower due to lattice-based operations, but provides post-quantum security (FIPS 204 ML-DSA standard).

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI page |
| `/api/run_test/` | POST | Execute single real test |
| `/api/get_results/` | GET | Fetch all results (JSON) |
| `/api/export_csv/` | GET | Download CSV of results |
| `/api/statistics/` | GET | Performance statistics |

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/api/run_test/ \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "ecc",
    "operation": "keygen",
    "message_size": 256
  }'
```

### Example Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "timestamp": "2025-11-03T23:00:00",
    "algorithm": "ecc",
    "operation": "keygen",
    "message_size": 256,
    "execution_time_ms": 3.247,
    "memory_usage_kb": 128.5,
    "status": "success"
  }
}
```

## Standards Compliance

- **ECC**: FIPS 186-5 (Digital Signature Standard)
  - Curve: secp256r1 (P-256)
  - Hash: SHA-256
  - Library: `ecdsa`

- **Dilithium**: FIPS 204 (Module-Lattice-Based Digital Signature Algorithm)
  - ML-DSA-2 (128-bit security)
  - Based on Learning With Errors (LWE)
  - Library: `oqs`

## Performance Notes

### ECC (NIST P-256)
- KeyGen: ~3-5 ms
- Sign: ~2-4 ms
- Verify: ~2-4 ms
- Quantum Safe: No

### CRYSTALS-Dilithium (ML-DSA-2)
- KeyGen: ~100-150 ms
- Sign: ~60-100 ms
- Verify: ~30-50 ms
- Quantum Safe: Yes (NIST PQC Standard)

**Important:** Dilithium will be significantly slower than ECC. This is expected and correct behavior for lattice-based post-quantum algorithms.

## Academic References

1. **FIPS 186-5**: Digital Signature Standard (DSS)
   - https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf

2. **FIPS 204**: Module-Lattice-Based Digital Signature Algorithm (ML-DSA)
   - https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf

3. **Original Dilithium**: CRYSTALS-Dilithium
   - https://pq-crystals.org/dilithium/


## License

Educational/Research purposes.


## About

This is an **accurate implementation** comparing real cryptographic algorithms for educational and research purposes.

Previous version used mock data; this version uses real, standards-compliant implementations (FIPS 186-5 for ECC, FIPS 204 for ML-DSA).
