"""Real current full snapshot and new-only native inputs; old run namespace absent."""
import unittest
from pg2102_current_newrun_native_qualification import source


class Qualification(unittest.TestCase):
    def test_actual_new_inputs_and_fixed_main_source_join(self):
        raw=source()
        for marker in ['pg2100-current-newrun-native-catalog-v1','pg2102-current-newrun-native-qualified-v1','pg1845-warning-unit-full-qualified-v1','qualify_snapshot()','len(catalog[\'selected\'])!=10']:
            self.assertTrue(marker in raw,marker)
        self.assertFalse('pg2046-receipt-preserving-current-native-catalog-v1'in raw)


if __name__=='__main__':unittest.main()
