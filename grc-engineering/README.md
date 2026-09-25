# grc-engineering

A daily practice repo: small, working GRC engineering builds — continuous control monitoring, evidence collection, access reviews, vendor risk, and AI governance tooling. Built to prove in-house operator skill, not consultant checklists.

## Project log

| Day | Project | What it proves |
|-----|---------|----------------|
| 01 | [AWS control health check](projects/01-aws-control-health-check) | Continuous monitoring: S3 encryption, public exposure, stale IAM keys — control tests you can run between audits |

## How to run

Each project is self-contained in `projects/<name>/` with its own README. Python 3.10+.
Most checks accept a `--demo` flag so they run on sample data without cloud credentials.
