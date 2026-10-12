"""Actual two-source namespace runs without old admission; typed rejection and gate."""
import copy
import inspect
import unittest
from pg1865_warning_direct_unused_dispatch import runtime_namespace,source,main,CANDIDATE,OLD,STAGE


class Entry(unittest.TestCase):
    def test_actual_namespace_fixed_sources_and_all_typed_negative_inputs(self):
        candidate={'actualExit':0,'candidateSource':CANDIDATE,'signatureVerified':True,'manifestSha256':'a'*64}
        before={'actualExit':0,'productionSource':OLD,'allClientAdvisoryFlock0':True,'genuineCompletion':{'managerFailureRetained':True},'privateBeforeSha256':'b'*64}
        ns=runtime_namespace(candidate,before)
        self.assertEqual(CANDIDATE,ns['SOURCE']);self.assertEqual('b'*64,ns['BASELINE_SHA'])
        self.assertIn('pg1860_parent_receipt.py',ns['sources']('a'*64))
        for key,bad in [('actualExit',True),('candidateSource',OLD),('signatureVerified',False),('manifestSha256',None)]:
            changed=copy.deepcopy(candidate);changed[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):runtime_namespace(changed,before)
        for key,bad in [('actualExit',1),('productionSource',CANDIDATE),('allClientAdvisoryFlock0',False),('privateBeforeSha256','x'),('genuineCompletion',None)]:
            changed=copy.deepcopy(before);changed[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):runtime_namespace(candidate,changed)
        for bad in [None,{},[]]:
            with self.assertRaises(ValueError):runtime_namespace(bad,before)
        self.assertIn('with management_gate',inspect.getsource(main));self.assertNotIn('prior.namespace',inspect.getsource(main))
        self.assertIn('pg1865-stage-v1.exit',source())
        self.assertIn('pg1865-fixed-stage-v1',STAGE);self.assertNotIn('pg1862-fixed-stage-v1',STAGE)


if __name__=='__main__':unittest.main()
