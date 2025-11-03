# ECC vs CRYSTALS-Dilithium — Django Web App

A minimal Django web application that demonstrates and compares cryptographic operations between ECC (NIST P-256) and CRYSTALS-Dilithium. The app provides an interactive UI to run mock benchmarks (time and memory), visualize averages, and export results to CSV.

## Features

- Interactive UI to run tests for:
  - Key generation
  - Message signing
  - Signature verification
- Live table of results and summary statistics
- Comparison bar chart (per operation)
- CSV export of collected results
- No external crypto dependency required (built-in mock controller)

## Project Structure

```
 ecc_vs_dilithium_analysis/
 ├─ ecc_vs_dilithium_analysis/          # Django project and app (single-app project)
 │  ├─ static/ecc_vs_dilithium_analysis/
 │  │  ├─ css/style.css
 │  │  └─ js/app.js
 │  ├─ templates/index.html             # Main UI
 │  ├─ controller.py                    # Mock TestController implementation
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

- Python 3.13 (or compatible with Django 5.2.x)
- Pip
- (Windows) PowerShell or Command Prompt

## Quick Start

1) Open the project directory:

```
cd ecc_vs_dilithium_analysis
```

2) Create and activate a virtual environment (recommended):

```
python -m venv venv
./venv/Scripts/Activate.ps1   # PowerShell
# or: .\venv\Scripts\activate.bat (cmd)
```

3) Install dependencies:

```
pip install -r requirements.txt
```

4) Apply database migrations (for Django built-in apps):

```
python manage.py migrate
```

5) Run the development server:

```
python manage.py runserver
```

Open the app at `http://127.0.0.1:8000/`.

## Usage

- Choose the algorithm (ECC or CRYSTALS-Dilithium).
- Select the operation: Key Generation, Message Signing, or Signature Verification.
- Adjust Message Size (bytes) and Iterations.
- Click Run Test. Results are appended to the table, statistics and chart update automatically.
- Use Export CSV to download a CSV of the current in-memory results.
- Use Clear to clear all results displayed in the UI.

Note: The backend uses a mock `TestController` to generate deterministic synthetic metrics; it does not require any external crypto library.

## API Endpoints

- `GET /` — Renders the main UI page
- `POST /api/run_test/` — Run a single test
  - JSON body: `{ "algorithm": "ecc"|"dilithium", "operation": "keygen"|"sign"|"verify", "message_size": <int> }`
  - Response: `{ status, data: { id, timestamp, algorithm, operation, message_size, execution_time_ms, memory_usage_kb, status } }`
- `GET /api/get_results/` — Returns all stored results (from DB)
- `GET /api/export_csv/` — Downloads CSV of all DB-stored results
- `GET /api/statistics/` — Returns aggregated averages for ECC and Dilithium

## Static Files

Static files live under the app at `static/ecc_vs_dilithium_analysis/...` and are referenced using Django's `{% static %}` template tag. During development, `DEBUG=True` serves them automatically.

## Common Tasks

- Create a superuser for admin:

```
python manage.py createsuperuser
```

- Access Django admin at `http://127.0.0.1:8000/admin/`.

## Notes

- This is a single-app Django project. The app name is `ecc_vs_dilithium_analysis` and it remains inside the same folder.
- For production, make sure to:
  - Set `DEBUG = False`
  - Configure `ALLOWED_HOSTS`
  - Serve static files using a proper web server or `collectstatic`
  - Use a production-grade WSGI/ASGI server

## License

Educational/demo purposes.
