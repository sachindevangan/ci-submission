import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

import requests

SIGNING_SECRET = os.environ.get("SIGNING_SECRET", "hello-there-from-b12")

now = datetime.now(timezone.utc)
timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"

payload = {
    "action_run_link": os.environ["ACTION_RUN_LINK"],
    "email": os.environ["APPLICANT_EMAIL"],
    "name": os.environ["APPLICANT_NAME"],
    "repository_link": os.environ["REPOSITORY_LINK"],
    "resume_link": os.environ["RESUME_LINK"],
    "timestamp": timestamp,
}

# Canonicalized: compact separators, keys sorted alphabetically, UTF-8 encoded
body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

# HMAC-SHA256 signature
mac = hmac.new(SIGNING_SECRET.encode("utf-8"), body, hashlib.sha256)
signature = mac.hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-Signature-256": f"sha256={signature}",
}

response = requests.post("https://b12.io/apply/submission", data=body, headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nSubmission receipt: {data.get('receipt')}")
else:
    raise SystemExit(f"Submission failed: {response.status_code} {response.text}")
