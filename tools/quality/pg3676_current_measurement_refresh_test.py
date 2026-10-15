"""No new acceptance/scope/cost; current20/18/XML deltas and exact safe case boundary."""
import copy
import json
import unittest
import pg3676_current_measurement_refresh as p
import pg3670_current_browser_public_receipts as publication


class Refresh(unittest.TestCase):
    def test_only_two_metadata_files_no_acceptance_or_scope_changes(self):
        texts={n:(p.PMO/n).read_text()for n in p.NAMES};updated=p.candidates(texts)
        self.assertEqual(texts[p.NAMES[0]],updated[p.NAMES[0]])
        self.assertEqual(texts[p.NAMES[1]],updated[p.NAMES[1]])
        old_inventory=json.loads(texts[p.NAMES[2]]);new_inventory=json.loads(updated[p.NAMES[2]])
        self.assertEqual(old_inventory['artifacts'],new_inventory['artifacts'])
        old=json.loads(texts[p.NAMES[3]]);new=json.loads(updated[p.NAMES[3]])
        self.assertEqual(old['formal'],new['formal']);self.assertEqual(old['wholeEffortCompletionRate'],new['wholeEffortCompletionRate'])
        self.assertEqual({r['id']:r['acceptance']for r in old['rows']},{r['id']:r['acceptance']for r in new['rows']})
        runtime={r['id']:r for r in new['rows']if r['id']in {'WBS-N09','WBS-N14'}}
        for row in runtime.values():
            self.assertEqual('VM_STEP_VERIFIED',row['measurementStatus']);self.assertFalse(row['currentLiveAuthority']);self.assertEqual('NOT_ACCEPTED',row['acceptance']['status'])
        self.assertEqual({'LINE':147,'METHOD':24,'CLASS':4,'BRANCH':10},new['currentBrowserResumeAndRuntimeClosure20261016']['deltaFromPriorCurrent'])

    def test_existing_binding_replay_refused(self):
        texts={n:(p.PMO/n).read_text()for n in p.NAMES};snapshot=json.loads(texts[p.NAMES[3]]);snapshot['measurementRun']='PG3632-current-native-measurement-v1';texts[p.NAMES[3]]=json.dumps(snapshot)
        with self.assertRaises(ValueError):p.candidates(texts)

    def test_safe_case_rejects_arbitrary_field_source_or_value(self):
        value=json.loads((p.W/'pg3580-current-browser-business-actual-v1/cases/PT-NBR-001.safe.json').read_bytes())
        self.assertEqual(value,publication.case_projection(value,1))
        bad=[]
        x=copy.deepcopy(value);x['session']='synthetic-forbidden';bad.append(x)
        x=copy.deepcopy(value);x['source']='foreign';bad.append(x)
        x=copy.deepcopy(value);x['readOnlyJcaCredentialQualified']='synthetic-secret';bad.append(x)
        x=copy.deepcopy(value);x['formalAccepted']=True;bad.append(x)
        for x in bad:
            with self.assertRaises(ValueError):publication.case_projection(x,1)


if __name__=='__main__':unittest.main()
