import unittest
import copy
import json
import subprocess
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


class ActualOriginalCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts={name:(trace.PMO/name).read_text()for name in trace.NAMES}
        cls.head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=trace.ROOT,text=True).strip()
        saved=json.loads(cls.texts[trace.NAMES[2]])
        old='b4230118efcc429ee29d6e6f5761c55175f1e85e'
        if saved['currentPhysicalCandidate']['source']!=old:
            prior=[r for r in saved['currentPhysicalCandidateHistory']if r['source']==old]
            if len(prior)!=1:raise ValueError('one preserved original before-candidate fixture')
            cls.head=prior[0]['metadataSource']
            cls.texts={name:subprocess.check_output(['git','show',cls.head+':documents/400_PGPT/470_PMO/'+name],cwd=trace.ROOT,text=True)for name in trace.NAMES}
        cls.proposed,cls.observed=trace.candidates(cls.texts,cls.head)
        cls.inventory=json.loads(cls.proposed[trace.NAMES[2]])

    def test_exact943_original4043_and_immutable_history_cost_acceptance(self):
        old=json.loads(self.texts[trace.NAMES[2]])
        self.assertEqual(old['artifacts'],self.inventory['artifacts'])
        self.assertEqual(old['measurementBindings'],self.inventory['measurementBindings'])
        self.assertEqual((943,4043,607,0),(self.observed['physicalArtifacts'],self.observed['tests'],self.observed['suites'],self.observed['acceptedLeafDelta']))
        self.assertEqual({'LINE':3554,'METHOD':687,'CLASS':38,'BRANCH':723},self.observed['remaining'])
        self.assertEqual(trace.SOURCE,self.inventory['currentPhysicalCandidate']['source'])
        for name in trace.NAMES[:2]:self.assertEqual(self.texts[name],self.proposed[name])
        before=json.loads(self.texts[trace.NAMES[3]]);after=json.loads(self.proposed[trace.NAMES[3]])
        for key in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate'):
            self.assertEqual(before[key],after[key])

    def test_wrong_bytes_missing_duplicate_acceptance_measurement_cost_rejected(self):
        changes=(lambda c:c['artifacts'].pop(),lambda c:c['artifacts'].append(copy.deepcopy(c['artifacts'][0])),
            lambda c:c['artifacts'][0].update(sha256='a'*64),lambda c:c.update(acceptedLeafDelta=1),
            lambda c:c['artifacts'][-1].update(additionalBudgetPp=1),
            lambda c:c['measurement'].update(sha256='b'*64),lambda c:c.update(effortPercent=100))
        for i,change in enumerate(changes):
            bad=copy.deepcopy(self.inventory);change(bad['currentPhysicalCandidate'])
            with self.subTest(vector=i),self.assertRaises(ValueError):trace.trace.verify_candidate(bad)


if __name__=='__main__':unittest.main()
