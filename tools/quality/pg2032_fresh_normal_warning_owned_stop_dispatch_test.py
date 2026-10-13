"""Actual staged/prequalification strings and flat current post envelope, no old slot/boot commands."""
import ast
import inspect
import unittest
from pyflakes.api import check
from pg2032_fresh_normal_warning_owned_stop_dispatch import STAGE,PARENT_PREQUAL,run_action


class Dispatch(unittest.TestCase):
    def test_actual_sources_and_qualification_contract(self):
        self.assertEqual(0,check('GUEST="fixed"\nHASHES={}\n'+PARENT_PREQUAL,'<actual state18/config2 new profile>'))
        self.assertEqual(0,check('DIGEST="fixed"\nFILES={}\n'+STAGE,'<actual immutable stage>'))
        self.assertTrue("helper.parent_state()"in PARENT_PREQUAL)
        self.assertTrue("'normalUnit0or10':True"in PARENT_PREQUAL)
        self.assertTrue('pg2032-fixed-stage-v1'in STAGE)
        self.assertTrue('pg2030-fresh-normal-warning-owned-stop-tools-v1'in STAGE)
        ast.parse(inspect.getsource(run_action))


if __name__=='__main__':unittest.main()
