import unittest
from pyflakes.api import check
import pg5948_private_lock3973_public as t


class OriginalPrivateLockProjectionTest(unittest.TestCase):
    def test_namespace_original_artifacts_and_current_counter_property(self):
        raw = t.payload({})
        self.assertIn('PG5944', raw); self.assertNotIn('PG5926', raw)
        self.assertNotIn('Popen', raw); self.assertNotIn('subprocess.run', raw)
        raw = t.operator_source()
        self.assertIn("public = base/'PG5944-current3973-cases'", raw)
        self.assertIn('privateLock34TargetFour100', raw)
        self.assertEqual(0, check('import json,hashlib,os\nW=QUALIFIED=SOURCE=ROOT=added_cases=payload=run=copy=terminal_trace=None\n'+raw, '<pure projection operator fixture>'))


if __name__ == '__main__':
    unittest.main()
