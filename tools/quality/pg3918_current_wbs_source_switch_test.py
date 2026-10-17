"""Exact17 only, all historical records/budget preserved and malformed source bridge refused."""
import copy
import json
import subprocess
import unittest
import pg3918_current_wbs_source_switch as switch


class ExistingSourceBridge(unittest.TestCase):
    def inputs(self):
        # BUG1394: all four original bytes match the actual criterion beforehashes.
        ref='189da545d0b938c7e2a0a09d5602284e6b4de6fb:documents/400_PGPT/470_PMO/'
        return {n:subprocess.check_output(['git','show',ref+n],cwd=switch.ROOT,text=True)for n in switch.NAMES},switch.review.read(switch.PROOF)

    def test_scope_budget_history_and_current_native_runtime(self):
        texts,proof=self.inputs();new=switch.candidates(texts,proof)
        self.assertEqual(texts[switch.NAMES[1]],new[switch.NAMES[1]])
        master=json.loads(new[switch.NAMES[0]]);old=json.loads(texts[switch.NAMES[0]])
        self.assertEqual(switch.review.EXPECTED,{r['id']for r in master['tasks']if r['acceptance']['status']=='ACCEPTED'})
        before={r['id']:r for r in old['tasks']}
        for row in master['tasks']:
            self.assertEqual(before[row['id']]['acceptance']['status'],row['acceptance']['status'])
            if row['id']in switch.review.EXPECTED:
                self.assertEqual(switch.SOURCE,row['acceptance']['source']);self.assertEqual(before[row['id']]['acceptance'],row['acceptanceHistory'][-1])
        inventory=json.loads(new[switch.NAMES[2]]);self.assertEqual(941,len(inventory['artifacts']));self.assertEqual(switch.SOURCE,inventory['source'])
        snapshot=json.loads(new[switch.NAMES[3]]);rows={r['id']:r for r in snapshot['rows']}
        for rid in ['WBS-N09','WBS-N14']:self.assertEqual('VM_STEP_VERIFIED',rows[rid]['measurementStatus']);self.assertFalse(rows[rid]['currentLiveAuthority'])
        for rid in ['WBS-N11','WBS-N12','WBS-N13','WBS-CHR-A01']:
            if before.get(rid):self.assertNotEqual('ACCEPTED',rows[rid].get('acceptance',{}).get('status'))
        self.assertIsNone(snapshot['wholeEffortCompletionRate']);self.assertIn('currentSourceRevalidation20261016',snapshot)
        self.assertEqual(260,snapshot['currentSourceRevalidation20261016PG3918']['physicalChanges'])
        self.assertEqual(18,snapshot['currentSourceRevalidation20261016PG3918']['latestNativeStreams'])

    def test_incomplete_criteria_source_hash_and_scope_rejected(self):
        texts,proof=self.inputs()
        for mode in ['count','scope','hash']:
            wrong=copy.deepcopy(proof)
            if mode=='count':wrong['criteriaRevalidated']=50
            elif mode=='scope':wrong['rows'].pop('WBS-C04')
            else:wrong['beforeFileHashes'][switch.NAMES[0]]='0'*64
            with self.subTest(mode=mode),self.assertRaises(ValueError):switch.candidates(texts,wrong)


if __name__=='__main__':unittest.main()
