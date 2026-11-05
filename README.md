# Invoicing port (AEM local-review test project)

A legacy invoicing service is being ported to a new FastAPI service. The port
must match the legacy system exactly: same totals to the cent, same refusals
(status and body), same invoice numbering. That is checked by **live parity
tests** that call both services and compare their answers.

This repository exists to try AEM's local review end to end: the developer's
coding agent reviews a story branch with the whole repository in view, runs
the unit and parity tests, and submits the review and the JUnit report to AEM.

| | Where | Port |
|---|---|---|
| Legacy service (reference, do not change) | `legacy/` | 8081 |
| Target service (the port) | `app/` | 8080 |

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

python -m legacy.server --port 8081            # terminal 1: the legacy system
uvicorn app.main:app --port 8080               # terminal 2: the port

pytest tests/unit                              # unit tests
LEGACY_URL=http://127.0.0.1:8081 TARGET_URL=http://127.0.0.1:8080 \
  pytest tests/parity --junitxml=reports/parity.xml   # live parity
```

Parity tests are skipped when either service is not reachable; a skipped
test is "not run", never "passed".

See `docs/legacy-behaviour.md` for what the legacy system does, and
`docs/STORY.md` for the story to deliver.
