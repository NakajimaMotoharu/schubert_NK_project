"""Current generation, independent windows and no old archive/session union."""
import unittest
from pg1446_current_cold_stage import W
from pg2030_fresh_normal_warning_owned_stop_sources import TOOLS
from pg2042_fresh_normal_warning_native_catalog import catalog_source


class Catalog(unittest.TestCase):
    def test_actual_normal_root_window_and_26_archive_preservation(self):
        raw=catalog_source((W/TOOLS/'pg2030_parent_receipt.py').read_text())
        for required in ['ROOT_START=106318294326','ROOT_END=107890801314','len(old)==26','pg2030-native-stop-v1','pg2015-completed-run-fresh-resume-once-v1','d6efa3f26d864704b015faa0625da1c0','len(selected)==10',"completion['normalUnit0or10']is True"]:
            self.assertTrue(required in raw,required)
        for forbidden in ["completion['genuinePid1Failure']",'9adbf05a-61d0-408b-b51d-ab19c7e5b16a',"JOB_RESULT')=='failed'",'len(old)==20']:
            self.assertTrue(forbidden not in raw,'no old selection authority '+forbidden)


if __name__=='__main__':unittest.main()
