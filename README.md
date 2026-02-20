# RFQ API Test Automation

pytest test suite for RFQ API - tests 10 bugs (N1-N5 negative scenarios, P1-P5 positive scenarios).

## Project Structure

```
MilosMaticSetviTask/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI/CD
├── config/
│   └── config.py              # API endpoints and headers
├── utils/
│   ├── api_client.py          # API client with request logging
│   ├── logger.py              # Logging setup
│   └── helpers.py             # Assertion helpers
├── tests/
│   ├── test_data.json         # Test data (payloads, expected results)
│   ├── test_negative_scenarios.py  # N1-N5 tests
│   └── test_positive_scenarios.py  # P1-P5 tests
├── .env                       # Environment variables (API_KEY, BASE_URL)
├── pytest.ini                 # pytest config, markers
├── requirements.txt           # Dependencies
└── README.md
```

## Setup

**Requirements:**
- Python 3.8+

**Steps:**

1. Clone the repo
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in project root:
```
API_KEY=your_api_key_here
BASE_URL=https://intelligence-dev.setvi.com
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific category:
```bash
pytest -m negative          # N1-N5 only
pytest -m positive          # P1-P5 only
pytest -m severity_high     # High severity only
```

Run specific file:
```bash
pytest tests/test_negative_scenarios.py
pytest tests/test_positive_scenarios.py
```

Run in parallel (4 workers):
```bash
pytest -n 4
```

## Reports

HTML report (generated after each run):
```
reports/report.html
```

Logs (request/response details, response times):
```
logs/test_execution.log
```

Note: API key is not logged for security.

## Test Markers

| Marker | Description |
|--------|-------------|
| `negative` | API errors and validation (N1-N5) |
| `positive` | Wrong behavior when API works (P1-P5) |
| `severity_low/medium/high` | Bug severity |
| `priority_low/medium/high` | Bug priority |

## Test Results (12 tests)

**Negative Scenarios (N1-N5):**
- N1: Empty text returns 400 - PASS (API validates correctly)
- N2: Invalid URL returns 400 - PASS (API validates correctly)
- N3: Threshold parameter ignored - PASS (bug exists, returns products below threshold)
- N4: topK not respected - PASS (bug exists, returns more than topK)
- N5: Special chars break matching - PASS (bug exists, special characters handled)

**Positive Scenarios (P1-P5):**
- P1: Private label ranking flag has no effect - PASS (bug confirmed, flag changes order)
- P2: High % for irrelevant product - PASS (top result is relevant)
- P3: URL upload returns wrong content - PASS (validates extracted product relevance)
- P4: Percentage score inconsistent - XFAIL (bug confirmed: scores vary 99% -> 80% -> 99%)
- P5: Missing product fields - XFAIL (bug confirmed: missing price, inStock, imageUrl)

**Summary:** 10 passed, 2 xfailed (expected failures)

Note: XFAIL tests run and validate bugs exist, but don't fail CI pipeline.

## API Endpoints

- `POST /api/rfq/upload-free-text` - Match products from free text
- `POST /api/rfq/upload-url-html` - Match products from URL

## How Tests Work

Tests are data-driven using `tests/test_data.json`:

```json
{
  "n1_empty_text_cases": [{
    "payload": {
      "text": "",
      "topK": 3,
      "threshold": 0.5
    },
    "expected_status": 400,
    "expected_response": {
      "error_code": "BadRequest",
      "message_contains": "must not be null"
    },
    "desc": "empty text"
  }]
}
```

Each test:
1. Loads test cases from JSON
2. Parametrizes with `@pytest.mark.parametrize`
3. Sends request via `api_client` fixture
4. Validates status code and response fields
5. Logs results

## CI/CD

GitHub Actions workflow runs tests automatically on push/PR:
- Workflow: `.github/workflows/tests.yml`
- Requires GitHub Secrets: `API_KEY`, `BASE_URL`
- Generates test report artifact

## Troubleshooting

**401 Unauthorized** - Check API_KEY in `.env`

**Tests fail** - Check `logs/test_execution.log` or `reports/report.html`

**Import errors** - Run `pip install -r requirements.txt`