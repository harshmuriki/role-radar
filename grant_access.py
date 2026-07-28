"""Grant a signed-in Supabase user access to the private Role Radar dashboard."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from supabase import create_client

DEFAULT_SUPABASE_URL = "https://xcijdgzgecnizcwskzcb.supabase.co"


def load_local_env() -> None:
    """Load the ignored local .env file without adding another dependency."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        key, separator, value = line.partition("=")
        if separator and key and not key.lstrip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="Email address of a user who has already signed up")
    args = parser.parse_args()
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SUPABASE_SECRET_KEY is required.")
    client = create_client(os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL), secret_key)
    users_response = client.auth.admin.list_users()
    users = users_response.users if hasattr(users_response, "users") else users_response
    user = next((item for item in users if item.email and item.email.lower() == args.email.lower()), None)
    if not user:
        raise ValueError(f"No signed-up Supabase user found for {args.email}.")
    client.table("role_radar_admins").upsert({"user_id": str(user.id)}).execute()
    print(f"Granted Role Radar access to {args.email}.")


if __name__ == "__main__":
    main()
