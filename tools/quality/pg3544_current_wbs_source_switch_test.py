import copy
import json
import unittest
import pg3544_current_wbs_source_switch as switch


class SourceSwitchContract(unittest.TestCase):
    def inputs(self):
        return {n:(switch.PMO/n).read_text()for n in switch.NAMES},switch.review.read(switch.PROOF)

    def test_explicit17_proof_preserves_budget_history_and_unaccepted_outbox(self):
        texts,proof=self.inputs();candidate=switch.candidates(texts,proof)
        self.assertEqual(texts[switch.NAMES[1]],candidate[switch.NAMES[1]])
        master=json.loads(candidate[switch.NAMES[0]])
        accepted=[r for r in master['tasks']if r['acceptance']['status']=='ACCEPTED']
        self.assertEqual(switch.review.EXPECTED,{r['id']for r in accepted})
        for row in accepted:
            self.assertEqual(switch.SOURCE,row['acceptance']['source'])
            self.assertEqual(switch.review.PREVIOUS,row['acceptanceHistory'][-1]['source'])
        outbox=next(r for r in master['tasks']if r['id']=='WBS-P006-02')
        self.assertNotEqual('ACCEPTED',outbox['acceptance']['status'])
        snapshot=json.loads(candidate[switch.NAMES[3]]);rows={r['id']:r for r in snapshot['rows']}
        for rid in ['WBS-N09','WBS-N14']:
            self.assertEqual('HISTORICAL_VM_SUCCESS_RECHECK',rows[rid]['measurementStatus'])
            self.assertEqual(switch.review.PREVIOUS,rows[rid]['measurementSource'])
        self.assertIsNone(snapshot['wholeEffortCompletionRate'])
        self.assertFalse(snapshot['currentSourceRevalidation20261016']['F03Accepted'])

    def test_missing_criterion_hash_or_unauthorized_acceptance_scope_refused(self):
        texts,proof=self.inputs()
        for mutation in ['count','scope','hash']:
            value=copy.deepcopy(proof)
            if mutation=='count':value['criteriaRevalidated']=50
            elif mutation=='scope':value['rows'].pop('WBS-C04')
            else:value['beforeFileHashes'][switch.NAMES[0]]='0'*64
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):switch.candidates(texts,value)


if __name__=='__main__':unittest.main()
