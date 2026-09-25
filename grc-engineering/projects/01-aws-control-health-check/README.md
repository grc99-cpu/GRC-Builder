# Project 01 — AWS control health check

Point-in-time control tests against an AWS account, producing a dated control-test report. The point is the *cadence*: run it daily (cron, CI, Lambda) and compliance becomes monitored, not just assessed once a year.

## Controls

| ID | Control | Why it matters |
|----|---------|----------------|
| S3-ENC | Default encryption on all S3 buckets | Unencrypted-at-rest data is a top SOC 2 / ISO 27001 A.10.1 finding |
| S3-PUB | No publicly readable buckets | The classic "open S3 bucket" breach vector |
| IAM-STALE | No access key unused for 90+ days | Stale credentials are a standing privilege-escalation risk (CIS AWS 1.x) |

## Run it

```bash
python3 check.py --demo      # sample data, no credentials needed
python3 check.py             # your real AWS account (pip install -r requirements.txt first)
```

Writes `control-report-YYYY-MM-DD.md` next to the script. Exit code 1 if any control fails, so it plugs straight into CI.

## Sample output

```
# AWS control health check — 2026-09-24 19:40 UTC
**Result: FAIL** (2 of 3 controls failing)

- [PASS] **S3-ENC** — Default encryption enabled on all S3 buckets
- [FAIL] **S3-PUB** — No S3 bucket allows public read access
  - Finding: 1 bucket(s) publicly readable: marketing-assets
- [FAIL] **IAM-STALE** — No access key unused for 90+ days
  - Finding: 1 user(s) with stale keys: legacy-etl
```
