"""PT-DEP-997002/003: independent failure/identity and durable receipt oracle."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pg997_offline_preservation import qualified, write_new, run_step

class PreservationTest(unittest.TestCase):
    def test_only_both_success_and_exact_source_backing_identity_allow_boot(self):
        a=[1,2,40,4,5];b=[1,3,20,6,7]
        self.assertTrue(qualified(0,0,a,a,b,b))
        for convert,compare in [(1,0),(-25,None),(0,1),(None,0),(False,0),(0,False)]:
            self.assertFalse(qualified(convert,compare,a,a,b,b))
        for v in [None,[],[1,2,40,4,True],[1,2,-40,4,5]]:
            self.assertFalse(qualified(0,0,v,v,b,b))
        for pos in range(5):
            changed=a.copy();changed[pos]+=1
            self.assertFalse(qualified(0,0,a,changed,b,b))
            changed=b.copy();changed[pos]+=1
            self.assertFalse(qualified(0,0,a,a,b,changed))

    def test_failure_receipt_survives_and_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'failure.json';record={'convertExit':-25,'compareExit':None,'partialAccepted':False}
            write_new(p,record)
            self.assertEqual(record,json.loads(p.read_bytes()))
            with self.assertRaises(FileExistsError):write_new(p,{'convertExit':0})
            self.assertEqual(record,json.loads(p.read_bytes()))

    def test_launch_exception_records_fixed_type_not_raw_message(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with patch('pg997_offline_preservation.subprocess.run',side_effect=OSError('DO_NOT_EXPORT')):
                with self.assertRaises(OSError):run_step(['fixture'],p/'log','CONVERT')
            raw=(p/'failure.safe.json').read_text();record=json.loads(raw)
            self.assertEqual('OSError',record['exceptionType'])
            self.assertEqual('CONVERT',record['phase'])
            self.assertFalse(record['partialAccepted'])
            self.assertNotIn('DO_NOT_EXPORT',raw)

if __name__=='__main__':unittest.main()
