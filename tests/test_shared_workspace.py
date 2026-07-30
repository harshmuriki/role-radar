from pathlib import Path
import unittest


class PrivateWorkspaceMigrationTests(unittest.TestCase):
    def test_private_workspace_migration_restores_owner_policies(self):
        sql = Path("supabase/migrations/20260730130000_restore_private_workspaces.sql").read_text()
        self.assertIn('create policy "Allowed users manage own companies"', sql)
        self.assertIn('create policy "Allowed users read own runs"', sql)
        self.assertIn('create policy "Allowed users read own jobs"', sql)
        self.assertIn("(select auth.uid()) = user_id and public.role_radar_access_allowed()", sql)
        self.assertIn('drop policy if exists "Allowed users manage shared companies"', sql)
        self.assertIn('add primary key (user_id, id)', sql)


class PrivateWorkerTests(unittest.TestCase):
    def test_worker_loads_sources_for_the_requested_owner(self):
        source = Path("generate_jobs.py").read_text()
        self.assertIn('.eq("user_id", user_id)', source)
        self.assertIn('select("id, user_id")', source)
        self.assertIn('run_scan(request["user_id"])', source)
        self.assertIn('on_conflict="user_id,id"', source)
        self.assertIn('.delete()\n        .eq("user_id", user_id)', source)


if __name__ == "__main__":
    unittest.main()
