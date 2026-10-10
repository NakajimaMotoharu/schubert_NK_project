import copy
import unittest
from pg1267_fresh_before_provenance import verify, FIELDS, SOURCE, SHA


class BeforeProvenanceTest(unittest.TestCase):
    def test_actual_closed_schema_and_separate_source_authority(self):
        snap={k:{} for k in FIELDS};snap['rows']={str(i):[] for i in range(24)}
        receipt={'actualExit':0,'productionSource':SOURCE,'privateBeforeSha256':SHA,'ordinaryNoargs':True,'newJstDate':'2026-10-11'}
        self.assertEqual(verify(receipt,snap)['beforeSchemaFields'],11)
        for key in receipt:
            for value in (None,False,'foreign'):
                bad=dict(receipt);bad[key]=value
                with self.assertRaises(ValueError):verify(bad,snap)
        for key in FIELDS:
            bad=dict(snap);bad.pop(key)
            with self.assertRaises(ValueError):verify(receipt,bad)
        for bad in (None,dict(snap,source=SOURCE),dict(snap,rows={}),dict(snap,rows={'a':None})):
            with self.assertRaises(ValueError):verify(receipt,bad)
        with self.assertRaises(ValueError):verify(None,snap)
        self.assertEqual(verify(copy.deepcopy(receipt),copy.deepcopy(snap))['sealedBeforeSha256'],SHA)


if __name__=='__main__':unittest.main()
