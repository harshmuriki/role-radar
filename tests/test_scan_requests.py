import unittest
from unittest.mock import patch

from generate_jobs import process_queued_scans


class FakeQuery:
    def __init__(self, data=None):
        self.data = data or []

    def select(self, *_args):
        return self

    def eq(self, *_args):
        return self

    def update(self, payload):
        self.payload = payload
        return self

    def execute(self):
        return type("Response", (), {"data": self.data})()


class FakeClient:
    def __init__(self):
        self.requests = FakeQuery([{"id": "request-1"}])
        self.updates = []

    def table(self, name):
        if name == "role_radar_scan_requests":
            query = self.requests
            original_update = query.update

            def update(payload):
                self.updates.append(payload)
                return original_update(payload)

            query.update = update
            return query
        raise AssertionError(f"Unexpected table: {name}")


class ProcessQueuedScansTests(unittest.TestCase):
    @patch("generate_jobs.worker_user_id", return_value="user-1")
    @patch("generate_jobs.create_client")
    def test_marks_a_queued_scan_completed_after_running_it(self, create_client, _worker_user_id):
        client = FakeClient()
        create_client.return_value = client
        calls = []

        process_queued_scans(lambda: calls.append("scan"))

        self.assertEqual(calls, ["scan"])
        self.assertEqual(client.updates[0]["status"], "running")
        self.assertEqual(client.updates[-1]["status"], "completed")
        self.assertIn("completed_at", client.updates[-1])


if __name__ == "__main__":
    unittest.main()
