import unittest
import copy
from unittest.mock import patch
import pg6306_current4043_trace as trace
import pg6308_current4043_static_plan as plan
import pg6310_web321_static_reviews as review
from static_disposition_overlay import load
from pyflakes.api import checkPath


class FixedDefinitions(unittest.TestCase):
    def test_exact4043_run_and_no_old_measurement(self):
        scope=trace.definitions('a'*64,'b'*64);values=scope['measurement'].__code__.co_consts
        for value in (4043,607,'PG6302-six-v1'):self.assertIn(value,values)
        for value in (3985,4034,4040,606,'PG6244-six-v1'):self.assertNotIn(value,values)
        self.assertEqual(trace.SOURCE,scope['SOURCE'])
        self.assertIn('PG6306-current943-trace-v1',scope['report'].__code__.co_consts)

    def test_all1357_and_fourteen_prior_unresolved_sites_preserved(self):
        rows,value=plan.calculate()
        self.assertEqual(1357,len(rows));self.assertEqual(1357,len({r['findingId']for r in rows}))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':980,'NOT_REVIEWED_CURRENT_SOURCE':377},value['statusCounts'])
        held=[r for r in rows if r.get('wholeSourceQualifiedCaseBindingStillPending')]
        self.assertEqual(14,len(held))
        for r in held:self.assertEqual('SOURCE_REBOUND_CURRENT_WHOLE_PENDING',r['status']);self.assertEqual([],r['currentWholeCaseRefs'])

    def test_prior_pending_without_explicit_unresolved_condition_rejected(self):
        rows=copy.deepcopy(load(plan.PRIOR,plan.PRIOR_SHA,plan.OLD))
        next(r for r in rows if r['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING')['wholeSourceQualifiedCaseBindingStillPending']=False
        with patch.object(plan,'load',return_value=rows),self.assertRaisesRegex(ValueError,'explicit prior unresolved'):
            plan.calculate()

    def test_exact20_individual_source_reasons_stay_whole_pending(self):
        rows,value=review.calculate()
        self.assertEqual(20,len(rows));self.assertEqual(20,len({r['findingId']for r in rows}))
        self.assertEqual(357,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertFalse(value['F03Accepted']);self.assertEqual(0,value['testsExecuted'])
        for r in rows:self.assertTrue(r['currentWholeJoinPending']);self.assertEqual([],r['currentWholeCaseRefs'])
        for path in (trace.__file__,plan.__file__,review.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
