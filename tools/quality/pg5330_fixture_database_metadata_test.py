import subprocess
import tempfile
import unittest
from pathlib import Path
import pg5330_fixture_database_metadata as metadata


class FixtureMetadata(unittest.TestCase):
    def test_missing_invalid_and_failed_observations_are_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError): metadata.capture(root, {})
            binary = root / 'lib/postgresql/18/bin/postgres'
            binary.parent.mkdir(parents=True); binary.write_bytes(b'fixture-not-executed')
            for code, version in [(1, 'postgres (PostgreSQL) 18.6'), (0, 'unknown'),
                                  (0, 'postgres (PostgreSQL) 18.6\nextra')]:
                with self.assertRaises(ValueError):
                    metadata.capture(root, {}, lambda *a, **k: subprocess.CompletedProcess(a, code, version, ''))

    def test_current_probe_does_not_assert_historical_or_original_db_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); binary = root / 'lib/postgresql/18/bin/postgres'
            binary.parent.mkdir(parents=True); binary.write_bytes(b'abc')
            def probe(command, **options):
                self.assertEqual(command, [str(binary), '--version'])
                self.assertEqual(options['timeout'], 10)
                return subprocess.CompletedProcess(command, 0, 'postgres (PostgreSQL) 18.6\n', '')
            value = metadata.capture(root, {'dev.codex.schubert.nk.api.file.ServiceProcessResourcesTest': 'bootstrap'}, probe)
            self.assertEqual(value['postgresSha256'], 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            self.assertTrue(value['isolatedFixtureDatabaseSelected'])
            self.assertFalse(value['historicalRunQualification'])
            self.assertEqual(value['originalOrVmDatabaseActions'], 0)


if __name__ == '__main__': unittest.main()
