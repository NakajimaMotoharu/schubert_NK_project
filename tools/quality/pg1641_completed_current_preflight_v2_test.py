"""Literal actual saved-schema and independent current native verifier tests."""
import unittest
from pyflakes.api import check
import pg1641_completed_current_preflight_v2 as p


class ActualSchemaTest(unittest.TestCase):
    def test_actual_schema_and_missing_foreign_null_rejected(self):
        keys = ['backup', 'configuration', 'extraDurable', 'originals', 'pid1', 'rows', 'runtime', 'startup', 'unitFilesActual', 'units']
        value = {k: [] if k == 'pid1' else {} for k in keys}
        self.assertTrue(p.validate_schema(value))
        for k in keys:
            bad = dict(value)
            del bad[k]
            with self.assertRaises(ValueError):
                p.validate_schema(bad)
            bad = dict(value)
            bad[k] = None
            with self.assertRaises(ValueError):
                p.validate_schema(bad)
        for bad in [None, {**value, 'native': {}}, {**value, 'foreign': {}}]:
            with self.assertRaises(ValueError):
                p.validate_schema(bad)

    def test_complete_generated_catalog_and_no_authority(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual current schema/native complete verifier>'))
        self.assertNotIn("native==after['native']", raw)
        for literal in ['independent_native_catalog()', "len(independent['selected'])==8", "len(independent['excludedHistorical'])==6", 'pg1641-completed-current-before-v2', "==after['runtime']", 'len(rows)==24']:
            self.assertIn(literal, raw)
        for operation in ['systemctl start', 'systemctl stop', 'daemon-reload', 'StartupPermitFiles', 'INSERT INTO', 'UPDATE schubert']:
            self.assertNotIn(operation, raw)


if __name__ == '__main__':
    unittest.main()
