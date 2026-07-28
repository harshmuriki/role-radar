"""Grant a signed-in Supabase user access to the private Role Radar dashboard."""

from __future__ import annotations

import argparse
import os

from supabase import create_client

DEFAULT_SUPABASE_URL = "https://xcijdgzgecnizcwskzcb.supabase.co"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="Email address of a user who has already signed up")
    args = parser.parse_args()
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SUPABASE_SECRET_KEY is required.")
    client = create_client(os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL), secret_key)
    users = client.auth.admin.list_users().users
    user = next((item for item in users if item.email and item.email.lower() == args.email.lower()), None)
    if not user:
        raise ValueError(f"No signed-up Supabase user found for {args.email}.")
    client.table("role_radar_admins").upsert({"user_id": str(user.id)}).execute()
    print(f"Granted Role Radar access to {args.email}.")


if __name__ == "__main__":
    main()
