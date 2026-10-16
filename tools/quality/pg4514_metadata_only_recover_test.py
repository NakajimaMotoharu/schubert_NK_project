"""All metadata-recovery and post dependencies must be typed and genuine."""
import copy
import unittest
import pg4514_metadata_only_recover as entry
from pg4494_inspect_pair_recover_test import RecoveryReceipt


class MetadataReceipt(unittest.TestCase):
    def fixture(self):
        v=RecoveryReceipt().fixture();v.pop('candidatePlaced');v['signalsIssued']=1;v['childSignalsIssued']=0;v['oldPostReplayed']=False;return v

    def test_complete_and_every_missing_or_type_mismatched_dependency(self):
        self.assertEqual(self.fixture(),entry.complete(self.fixture()))
        for level in ['outer','post']:
            v=self.fixture()
            for key in (v if level=='outer'else v['independentPost']):
                bad=copy.deepcopy(v);target=bad if level=='outer'else bad['independentPost'];del target[key]
                with self.subTest(level=level,key=key),self.assertRaises(ValueError):entry.complete(bad)
            bad=copy.deepcopy(v);target=bad if level=='outer'else bad['independentPost'];target['actualExit']=False
            with self.assertRaises(ValueError):entry.complete(bad)

    def test_one_signal_no_child_or_replay_and_current_frame_sequence(self):
        for key,value in [('signalsIssued',0),('signalsIssued',2),('childSignalsIssued',1),('oldPostReplayed',True),('oldScopesNormal',True)]:
            v=self.fixture();v[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):entry.complete(v)
        raw=entry.main_source();compile(raw,'<actual metadata observer>','exec')
        self.assertIn('SSC298_METADATA_READY',raw);self.assertIn('SSC298_METADATA_GONE',raw)
        self.assertNotIn('SSC297_PAIR_GONE',raw);self.assertNotIn('originalInspectActualExit',raw)


if __name__=='__main__':unittest.main()
