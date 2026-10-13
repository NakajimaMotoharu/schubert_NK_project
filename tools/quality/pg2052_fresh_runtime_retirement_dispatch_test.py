"""Actual stage/source/BOM and current17 entry profile before any owner or unlink/reload."""
import unittest
from pyflakes.api import check
from pg2052_fresh_runtime_retirement_dispatch import STAGE,PARENT_PREQUAL,TOOLS


class Entry(unittest.TestCase):
    def test_current_seventeen_file_stage_and_parent_profile(self):
        self.assertEqual(0,check('DIGEST="fixed"\nFILES={}\n'+STAGE,'<current runtime stage>'))
        self.assertEqual(0,check('GUEST="fixed"\nHASHES={}\n'+PARENT_PREQUAL,'<current parent prequal>'))
        self.assertTrue('pg2052-fixed-stage-v1'in STAGE and TOOLS+'.tar'in STAGE)
        self.assertTrue('PG1846'in STAGE and '0fd734195b4d5338f6b7e860e087cce561d49562'in STAGE)
        self.assertTrue('PG1638'not in STAGE)
        self.assertTrue('pg2050_native_owned_stop'in PARENT_PREQUAL)


if __name__=='__main__':unittest.main()
