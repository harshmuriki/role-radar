"""Always-on local worker that executes dashboard-requested tests and full scans."""
import argparse
import os
import subprocess
import sys
import time
from generate_jobs import ROOT, load_local_env, process_queued_scans, process_queued_tests


def run_full_scan(user_id: str) -> None:
    env = dict(os.environ, ROLE_RADAR_USER_ID=user_id)
    subprocess.run([sys.executable, str(ROOT / "generate_jobs.py")], check=True, env=env)


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    interval = max(1, int(os.getenv("POLL_INTERVAL_SECONDS", "3")))
    while True:
        try:
            process_queued_tests()
            process_queued_scans(run_full_scan)
        except Exception as exc:
            print(f"Worker error: {exc}", flush=True)
        if args.once:
            break
        time.sleep(interval)


if __name__ == "__main__":
    main()
