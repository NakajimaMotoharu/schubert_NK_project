import unittest
import pg6076_jms_owner_qualification as t
from pg6054_expiry_read_qualification import actual_original, MODULES


class ExplicitCurrentSelectionDimensionsTest(unittest.TestCase):
    def test_generic_verdict_requires_current_source_and_all_six_actual_static(self):
        expected = {'public.Fixture': {'one'}}
        begin = dict(source=t.SOURCE, expectedTests=1933, expected={'public.Fixture': ['one']})
        manifest = dict(source=t.SOURCE, actualExit=0, mavenActualExit=0, phaseExits=[0, 0],
            exactInventory=True, sourceFixed=True, selectedQualified=True, failedOrSkipped=[],
            tests=1933, suites=317, staticIssues={m: 0 for m in MODULES})
        actual_original(manifest, begin, expected, t.SOURCE, (1933, 317))
        for wrong in (dict(manifest, source='old-source'), dict(manifest, tests=1932),
                      dict(manifest, staticIssues={m: 0 for m in MODULES[:-1]})):
            with self.assertRaises(ValueError):
                actual_original(wrong, begin, expected, t.SOURCE, (1933, 317))


if __name__ == '__main__':
    unittest.main()
