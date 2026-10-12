"""Actual producer gate is placed before Java owner entry and exact class marker."""
import unittest
from pg1875_warning_ro_marker_dispatch import source,STAGE,REMOTE


class Gate(unittest.TestCase):
    def test_actual_composed_entry_real_prequal_before_class_operation(self):
        raw=source()
        self.assertIn('pg1873-frozen-v1.safe.json',raw)
        self.assertIn('pg1875-actual-marker-prequal-v1.safe.json',raw)
        self.assertLess(raw.index('check=subprocess.run'),raw.index('for clazz in'))
        self.assertIn("expected=b'PG1872_INPUT_CLOSURE_READY\\n'",raw)
        self.assertIn('pg1875-stage-v1.exit',raw)
        self.assertIn(REMOTE,STAGE)


if __name__=='__main__':unittest.main()
