import copy
import json
import unittest
from pg2414_question_unused_dispatch import source,STAGE,GUEST,REMOTE,runtime_namespace,W,BEFORE,production


class Dispatch(unittest.TestCase):
    def test_complete_new_immutable_slots_current_and_candidate(self):
        raw = source()
        for v in ['pg2413-frozen-v1.safe.json','pg2410-retired-current-before-v1',
                  'pg2428-manifest-v1.sig','0.1.0-PG2428','0.1.0-PG2126',
                  'pg2414-stage-v1.exit','Pg2412UnusedStage']:
            self.assertIn(v,raw)
        for v in ['pg2134-','pg2133-frozen','daemon-reload','StartUnit(','StopUnit(']:
            self.assertNotIn(v,raw)
        self.assertIn('pg2414-fixed-stage-v1',STAGE)
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg2412-question-unused-tools-v1',GUEST)
        self.assertEqual('/home/ubuntu/pg2414-question-input-v1',REMOTE)

    def test_actual_retired_current_required_no_fallback(self):
        before=json.loads((W/'pg2410-retired-current-before-v1/manifest.safe.json').read_bytes())
        candidate={'actualExit':0,'candidateSource':production(),'signatureVerified':True,
                   'candidateNotDeployed':True,'manifestSha256':'a'*64}
        namespace=runtime_namespace(candidate,before)
        self.assertEqual(BEFORE,namespace['BASELINE_SHA'])
        self.assertEqual(production(),namespace['SOURCE'])
        for field in ['runtimeAlreadyRetired','productionSource','privateBeforeSha256',
                      'allClientAdvisoryFlock0','allTenUnitsKernelEmpty']:
            wrong=copy.deepcopy(before);wrong[field]=None
            with self.assertRaises(ValueError):
                runtime_namespace(candidate,wrong)
        for field in ['candidateSource','signatureVerified','candidateNotDeployed','actualExit']:
            wrong=dict(candidate);wrong[field]=None
            with self.assertRaises(ValueError):
                runtime_namespace(wrong,before)


if __name__ == '__main__':
    unittest.main()
