"""Independent owner/path candidate and fee-stage negative tests (tools only)."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pg996_v3_initial_join as subject

class JoinTest(unittest.TestCase):
    def test_present_candidate_is_not_contract_oracle_acceptance(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'X.java').write_bytes(b'fixture')
            w={'tasks':[{'id':'WBS-X','evidencePlan':{'candidateTestFiles':['XTest.java','YTest.java'],
              'designFiles':['SS-X.md'],'specDirectory':'spec'}}]}
            i={'requirements':[{'id':'R-001','owner':'WBS-X','source':'RD.md','designTrace':'trace.md'}],
               'artifacts':[{'path':'X.java','owner':'WBS-X','costOwner':'WBS-X',
                 'sha256':'f16d05ec6b29248d2c61adb1e9263f78e4f7b7bb6274afb7764b4e1d6bfffe4d'}]}
            with patch.object(subject,'ROOT',root): req,art=subject.build_join(w,i)
            self.assertEqual(['XTest.java'],art[0]['candidateTests'])
            self.assertTrue(art[0]['present'])
            self.assertFalse(art[0]['sameInventoryByte'])
            self.assertFalse(art[0]['independentOracleVerified'])
            self.assertFalse(art[0]['contractAccepted'])
            self.assertFalse(req[0]['contractAccepted'])

    def test_unknown_owner_and_missing_file_do_not_invent_mapping(self):
        with tempfile.TemporaryDirectory() as d,patch.object(subject,'ROOT',Path(d)):
            req,art=subject.build_join({'tasks':[]},{'requirements':[],
              'artifacts':[{'path':'absent','owner':'WBS-UNKNOWN','costOwner':'WBS-UNKNOWN','sha256':'none'}]})
            self.assertEqual([],req)
            self.assertFalse(art[0]['present'])
            self.assertEqual([],art[0]['candidateTests'])
            self.assertEqual([],art[0]['designFiles'])
            self.assertIsNone(art[0]['specDirectory'])

if __name__=='__main__': unittest.main()
