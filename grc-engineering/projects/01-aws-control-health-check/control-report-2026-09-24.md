# AWS control health check — 2026-09-25 00:35 UTC
**Result: FAIL** (3 of 3 controls failing)

- [FAIL] **S3-ENC** — Default encryption enabled on all S3 buckets
  - Finding: 1 bucket(s) without default encryption: logs-archive
- [FAIL] **S3-PUB** — No S3 bucket allows public read access
  - Finding: 1 bucket(s) publicly readable: marketing-assets
- [FAIL] **IAM-STALE** — No access key unused for 90+ days
  - Finding: 1 user(s) with stale keys: legacy-etl
