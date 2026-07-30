import os
import unittest
from unittest.mock import patch

from generate_jobs import process_queued_scans


class FakeQuery:
    def __init__(self, data=None, updates=None):
        self.data = data or []
        self.updates = updates

    def select(self, *_args):
        return self

    def eq(self, *_args):
        return self

    def update(self, payload):
        if self.updates is not None:
            self.updates.append(payload)
        return self

    def execute(self):
        return type("Response", (), {"data": self.data})()


class FakeClient:
    def __init__(self):
        self.updates = []
        self.requests = FakeQuery([{"id": "request-1", "user_id": "user-1"}], self.updates)

    def table(self, name):
        if name == "role_radar_scan_requests":
            return self.requests
        raise AssertionError(f"Unexpected table: {name}")


class ProcessQueuedScansTests(unittest.TestCase):
    @patch.dict(os.environ, {"SUPABASE_SECRET_KEY": "test-key"})
    @patch("generate_jobs.create_client")
    def test_routes_each_queued_scan_to_the_requesting_owner(self, create_client):
        client = FakeClient()
        create_client.return_value = client
        calls = []

        process_queued_scans(lambda user_id: calls.append(user_id))

        self.assertEqual(calls, ["user-1"])
        self.assertEqual(client.updates[0]["status"], "running")
        self.assertEqual(client.updates[-1]["status"], "completed")
        self.assertIn("completed_at", client.updates[-1])


if __name__ == "__main__":
    unittest.main()
