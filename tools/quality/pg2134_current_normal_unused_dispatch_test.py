import copy
import json
import unittest
from pg2134_current_normal_unused_dispatch import source,STAGE,runtime_namespace,W,BEFORE,production

class DirectEntry(unittest.TestCase):
    def test_real_qualified_old_new_inputs_and_operational_namespace(self):
        a=json.loads((W/'pg2126-candidate-build-v1.safe.json').read_bytes())
        b=json.loads((W/'pg2130-current-normal-before-v1/manifest.safe.json').read_bytes())
        ns=runtime_namespace(a,b)
        self.assertEqual(production(),ns['SOURCE'])
        self.assertEqual(BEFORE,ns['BASELINE_SHA'])
        self.assertIn('pg2132-current-normal-unused-tools-v1',ns['GUEST'])
        raw=source()
        self.assertIn('pg2133-frozen-v1.safe.json',raw)
        self.assertIn('pg2130-current-normal-before-v1',raw)
        self.assertIn('pg2126-manifest-v1.sig',raw)
        self.assertIn('0.1.0-PG2126',raw)
        self.assertIn('0.1.0-PG1846',raw)
        self.assertIn('pg2134-stage-v1.exit',raw)
        self.assertNotIn('pg1865',raw)
        self.assertNotIn('PG1638',raw)
        self.assertNotIn('pg1865',STAGE)

    def test_wrong_current_or_non_normal_receipt_does_not_grant_namespace(self):
        a=json.loads((W/'pg2126-candidate-build-v1.safe.json').read_bytes())
        b=json.loads((W/'pg2130-current-normal-before-v1/manifest.safe.json').read_bytes())
        for field in ['productionSource','privateBeforeSha256','allTenUnitsKernelEmpty','allClientAdvisoryFlock0']:
            wrong=copy.deepcopy(b);wrong[field]=None
            with self.assertRaises(ValueError):runtime_namespace(a,wrong)
        for field in ['genuinePid1StartDone','normalUnit0or10','currentManagerGc']:
            wrong=copy.deepcopy(b);wrong['genuineCompletion'][field]=False
            with self.assertRaises(ValueError):runtime_namespace(a,wrong)

if __name__=='__main__':unittest.main()
