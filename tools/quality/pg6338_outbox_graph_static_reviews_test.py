import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6336_current4048_static_plan as plan
import pg6338_outbox_graph_static_reviews as review


class CurrentReauthentication(unittest.TestCase):
    def test_all1356_raw_and_fourteen_missing_refs_not_promoted(self):
        rows,value=plan.calculate()
        self.assertEqual(1356,len(rows));self.assertEqual(1356,len({r['findingId']for r in rows}))
        self.assertEqual(955,value['strictReboundPriorDecided']);self.assertEqual(14,value['priorUnresolvedRetained'])
        held=[r for r in rows if r.get('wholeSourceQualifiedCaseBindingStillPending')]
        self.assertEqual(14,len(held))
        for r in held:self.assertEqual('SOURCE_REBOUND_CURRENT_WHOLE_PENDING',r['status']);self.assertEqual([],r['currentWholeCaseRefs'])

    def test_individual44_all_current_owners_pinned_nine_context_only(self):
        rows,value=review.calculate()
        self.assertEqual(44,len(rows));self.assertEqual(44,len({r['findingId']for r in rows}))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':969,'NOT_REVIEWED_CURRENT_SOURCE':343,
            'REQUIRED_CONTRACT':35,'CONTEXT_NOT_APPLICABLE':9},value['statusCounts'])
        for r in rows:
            self.assertTrue(r['rawWarningRetained']);self.assertFalse(r['actualRuntimeProven'])
            self.assertTrue(r['currentWholeJoinPending']);self.assertEqual([],r['currentWholeCaseRefs'])
            if r['status']=='CONTEXT_NOT_APPLICABLE':
                self.assertEqual(review.T,r['rule']);self.assertTrue(r['staticContextPremiseOnly'])
                self.assertEqual([],r['plannedCurrentWholeCaseClasses'])
                self.assertEqual('7.28.0',r['pinnedRule']['version'])
            else:self.assertTrue(r['plannedCurrentWholeCaseClasses'])
        self.assertEqual(0,value['testsExecuted']);self.assertFalse(value['F03Accepted'])
        for path in (plan.__file__,review.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_one_missing_required_span_and_pending_without_flag_rejected(self):
        spec=copy.deepcopy(review.SPEC);del spec['WebLogReplayWorker'][(26,review.V)]
        with patch.object(review,'SPEC',spec),self.assertRaisesRegex(ValueError,'all44'):
            review.calculate()
        rows=copy.deepcopy(plan.load(plan.PRIOR,plan.PRIOR_SHA,plan.OLD))
        next(r for r in rows if r['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING')['wholeSourceQualifiedCaseBindingStillPending']=False
        with patch.object(plan,'load',return_value=rows),self.assertRaisesRegex(ValueError,'explicit prior unresolved'):
            plan.calculate()


if __name__=='__main__':unittest.main()
