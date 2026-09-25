#!/usr/bin/env python3
"""
Project 01 — AWS control health check
=====================================
Runs point-in-time control tests against an AWS account and emits a dated
control-test report. Designed to be scheduled (e.g. daily) so the compliance
posture is *monitored*, not just assessed once a year.

Controls tested:
  - S3-ENC: every bucket must have default server-side encryption enabled
  - S3-PUB: no bucket may allow public read access
  - IAM-STALE: no IAM access key may go 90+ days without being used

Usage:
  python check.py --demo          # run on built-in sample data (no credentials needed)
  python check.py                 # run against your own AWS account (needs boto3 + credentials)

Exit code is 0 when all controls pass, 1 when any control fails.
"""
import argparse
import datetime
import json
import sys

STALE_KEY_DAYS = 90

# ---------------------------------------------------------------- sample data
SAMPLE_S3 = [
    {"Name": "prod-app-data", "Encryption": True, "PublicRead": False},
    {"Name": "marketing-assets", "Encryption": True, "PublicRead": True},
    {"Name": "logs-archive", "Encryption": False, "PublicRead": False},
]
SAMPLE_IAM_KEYS = [
    {"User": "deploy-bot", "LastUsedDaysAgo": 2},
    {"User": "legacy-etl", "LastUsedDaysAgo": 214},
    {"User": "nabil.admin", "LastUsedDaysAgo": 12},
]


# ------------------------------------------------------------------- checks
def check_s3_encryption(buckets):
    failing = [b["Name"] for b in buckets if not b.get("Encryption")]
    return {
        "id": "S3-ENC",
        "name": "Default encryption enabled on all S3 buckets",
        "result": "PASS" if not failing else "FAIL",
        "finding": None if not failing else
                   f"{len(failing)} bucket(s) without default encryption: {', '.join(failing)}",
    }


def check_s3_public(buckets):
    failing = [b["Name"] for b in buckets if b.get("PublicRead")]
    return {
        "id": "S3-PUB",
        "name": "No S3 bucket allows public read access",
        "result": "PASS" if not failing else "FAIL",
        "finding": None if not failing else
                   f"{len(failing)} bucket(s) publicly readable: {', '.join(failing)}",
    }


def check_iam_stale_keys(keys):
    failing = [k["User"] for k in keys if k.get("LastUsedDaysAgo", 0) >= STALE_KEY_DAYS]
    return {
        "id": "IAM-STALE",
        "name": f"No access key unused for {STALE_KEY_DAYS}+ days",
        "result": "PASS" if not failing else "FAIL",
        "finding": None if not failing else
                   f"{len(failing)} user(s) with stale keys: {', '.join(failing)}",
    }


# ------------------------------------------------------------------ runners
def demo_run():
    return [check_s3_encryption(SAMPLE_S3), check_s3_public(SAMPLE_S3),
            check_iam_stale_keys(SAMPLE_IAM_KEYS)]


def aws_run():
    try:
        import boto3  # noqa
    except ImportError:
        sys.exit("boto3 is not installed. Run: pip install -r requirements.txt "
                 "or use --demo for sample data.")

    s3 = boto3.client("s3")
    buckets = []
    for b in s3.list_buckets()["Buckets"]:
        name = b["Name"]
        try:
            s3.get_bucket_encryption(Bucket=name)
            encrypted = True
        except Exception:
            encrypted = False
        try:
            acl = s3.get_bucket_acl(Bucket=name)
            public = any(
                g.get("Grantee", {}).get("URI", "").endswith("AllUsers")
                for g in acl.get("Grants", [])
            )
        except Exception:
            public = False
        buckets.append({"Name": name, "Encryption": encrypted, "PublicRead": public})

    iam = boto3.client("iam")
    keys = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for user in iam.list_users()["Users"]:
        uname = user["UserName"]
        for meta in iam.list_access_keys(UserName=uname)["AccessKeyMetadata"]:
            last = iam.get_access_key_last_used(AccessKeyId=meta["AccessKeyId"]) \
                     .get("AccessKeyLastUsed", {}).get("LastUsedDate")
            age = (now - last).days if last else 9999
            keys.append({"User": uname, "LastUsedDaysAgo": age})

    return [check_s3_encryption(buckets), check_s3_public(buckets),
            check_iam_stale_keys(keys)]


# ------------------------------------------------------------------- report
def render_report(results):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fails = [r for r in results if r["result"] == "FAIL"]
    lines = [f"# AWS control health check — {stamp}",
             f"**Result: {'FAIL' if fails else 'PASS'}** "
             f"({len(fails)} of {len(results)} controls failing)", ""]
    for r in results:
        icon = "[PASS]" if r["result"] == "PASS" else "[FAIL]"
        lines.append(f"- {icon} **{r['id']}** — {r['name']}")
        if r["finding"]:
            lines.append(f"  - Finding: {r['finding']}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true",
                        help="run on sample data instead of a real AWS account")
    args = parser.parse_args()

    results = demo_run() if args.demo else aws_run()
    report = render_report(results)
    print(report)

    out = f"control-report-{datetime.date.today().isoformat()}.md"
    with open(out, "w") as f:
        f.write(report)
    print(f"\nReport written to {out}")
    return 1 if any(r["result"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
