from pathlib import Path
import unittest


class CompanyUniquenessMigrationTests(unittest.TestCase):
    def test_migration_scopes_career_url_uniqueness_to_each_user(self):
        sql = Path("supabase/migrations/20260730110000_scope_company_urls_per_user.sql").read_text()
        self.assertIn("drop constraint if exists role_radar_companies_careers_url_key", sql)
        self.assertIn("unique (user_id, careers_url)", sql)


if __name__ == "__main__":
    unittest.main()
