import copy
import unittest
from unittest.mock import patch
import pg6278_current4040_static_plan as plan
import pg6280_outbox320_static_reviews as review
from static_disposition_overlay import load


class CurrentFacts(unittest.TestCase):
    def test_all1350_retained_and_fourteen_pending_not_promoted(self):
        rows,value=plan.calculate()
        self.assertEqual(1350,len(rows));self.assertEqual(1350,len({r['findingId']for r in rows}))
        self.assertEqual({'NOT_REVIEWED_CURRENT_SOURCE':504,'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':846},value['statusCounts'])
        held=[r for r in rows if r.get('wholeSourceQualifiedCaseBindingStillPending')]
        self.assertEqual(14,len(held))
        for r in held:
            self.assertEqual('SOURCE_REBOUND_CURRENT_WHOLE_PENDING',r['status'])
            self.assertEqual([],r['currentWholeCaseRefs']);self.assertTrue(r['currentWholeJoinPending'])

    def test_missing_explicit_prior_unresolved_condition_rejected(self):
        rows=copy.deepcopy(load(plan.PRIOR,plan.PRIOR_SHA,plan.OLD))
        next(r for r in rows if r['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING')['wholeSourceQualifiedCaseBindingStillPending']=False
        with patch.object(plan,'load',return_value=rows),self.assertRaisesRegex(ValueError,'only explicit prior unresolved'):
            plan.calculate()

    def test_all26_changed_owner_spans_and_exact25_original_refs(self):
        rows,value=review.calculate()
        self.assertEqual(26,len(rows));self.assertEqual(26,len({r['findingId']for r in rows}))
        self.assertEqual({'NOT_REVIEWED_CURRENT_SOURCE':478,'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':846,'REQUIRED_CONTRACT':26},value['statusCounts'])
        for r in rows:
            self.assertEqual(25,len(r['originalSelectedCaseRefs']))
            self.assertTrue(r['currentWholeJoinPending']);self.assertEqual([],r['currentWholeCaseRefs'])
            self.assertFalse(r['formalAccepted']);self.assertFalse(r['F03Accepted'])


if __name__=='__main__':unittest.main()
