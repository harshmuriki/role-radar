from pathlib import Path
import unittest


class SharedWorkspaceMigrationTests(unittest.TestCase):
    def test_migration_grants_allowlisted_users_shared_workspace_access(self):
        sql = Path("supabase/migrations/20260730120000_make_role_radar_shared_workspace.sql").read_text()
        self.assertIn('create policy "Allowed users manage shared companies"', sql)
        self.assertIn('create policy "Allowed users read shared runs"', sql)
        self.assertNotIn("= user_id and public.role_radar_access_allowed()", sql)


class SharedWorkerTests(unittest.TestCase):
    def test_worker_does_not_filter_companies_or_requests_by_owner(self):
        source = Path("generate_jobs.py").read_text()
        self.assertNotIn('.eq("user_id", user_id)', source)


if __name__ == "__main__":
    unittest.main()
