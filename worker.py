"""Always-on local worker that executes dashboard-requested company tests."""
import argparse
import os
import time
from generate_jobs import load_local_env, process_queued_tests

load_local_env()
parser = argparse.ArgumentParser()
parser.add_argument("--once", action="store_true")
args = parser.parse_args()
interval = max(1, int(os.getenv("POLL_INTERVAL_SECONDS", "3")))
while True:
    try:
        process_queued_tests()
    except Exception as exc:
        print(f"Worker error: {exc}", flush=True)
    if args.once:
        break
    time.sleep(interval)
