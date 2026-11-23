"""Offline migration source checks for SSC-479 and BUG-3722."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[4]
MODULE = ROOT / "src/schubert-nk-api"
MIGRATIONS = MODULE / "src/main/resources/db/migration"
FIXTURES = MODULE / "src/test/java/dev/codex/schubert/nk/api/database"


class RoutineDefaultsSourceTest(unittest.TestCase):
    def test_pt_db_acl031_s01_owner_database_default_revoke(self):
        resource = MIGRATIONS / "V031__restrict_routine_default_privileges.sql"
        source = resource.read_bytes()
        self.assertNotIn(b"\r", source)
        statements = [
            " ".join(statement.split()).upper()
            for statement in "\n".join(
                line for line in source.decode("utf-8").splitlines() if not line.startswith("--")
            ).split(";")
            if statement.strip()
        ]
        self.assertEqual(
            statements,
            [
                "SET ROLE NK_OWNER",
                "ALTER DEFAULT PRIVILEGES FOR ROLE NK_OWNER REVOKE EXECUTE ON ROUTINES FROM PUBLIC",
                "RESET ROLE",
            ],
        )

    def test_pt_db_acl031_s02_version_inventory_keeps_the_approved_sequence(self):
        expected = [f"{version:03}" for version in range(1, 32)]
        resource_versions = sorted(path.name[1:4] for path in MIGRATIONS.glob("V*.sql"))
        self.assertEqual(resource_versions, expected)
        independent_java = (FIXTURES / "MigrationInventory.java").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'"(\d{3})"', independent_java), expected)

    def test_pt_db_acl031_s03_all_versions_use_one_independent_count(self):
        source = (FIXTURES / "DatabaseMigrationTest.java").read_text(encoding="utf-8")
        fixture = source.split("void strictMigrationIsAppliedValidatedAndIdempotent()", 1)[1]
        fixture = fixture.split("@Test", 1)[0]
        self.assertIn(
            "assertEquals(MIGRATION_VERSIONS.size(), firstMigration.migrationsExecuted);", fixture
        )
        self.assertRegex(
            fixture,
            r"assertEquals\(\s*\(long\) MIGRATION_VERSIONS\.size\(\),\s*queryLong\("
            r"\s*ADMIN,\s*\"select count\(\*\) from schubert_meta.flyway_schema_history "
            r"where success and version is not null\"\)\)",
        )

    def test_pt_db_acl031_s04_cleanup_uses_the_independent_full_inventory(self):
        maintenance = FIXTURES.parent / "maintenance"
        source = (maintenance / "StepCleanupBoundaryTest.java").read_text(encoding="utf-8")
        fixture = source.split("void appendOnlyMigrationInventory()", 1)[1]
        fixture = fixture.split("\n  static long id", 1)[0]
        self.assertIn("assertEquals(MigrationInventory.VERSIONS, resourceVersions);", fixture)
        self.assertIn('MigrationInventory.COUNT_TEXT + "|1"', fixture)
        self.assertNotIn("files.getLast()", fixture)
        self.assertIn('"V029__strict_nullable_compound_checks.sql", files.get(28)', fixture)


if __name__ == "__main__":
    unittest.main()
