import unittest
import copy
import json
import subprocess
import pg6334_current4048_trace as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_exact4048_run_and_no_prior_measurement(self):
        scope=subject.definitions('a'*64,'b'*64);values=scope['measurement'].__code__.co_consts
        for value in (4048,607,'PG6330-six-v1'):self.assertIn(value,values)
        for value in (3985,4034,4040,4043,606,'PG6244-six-v1','PG6302-six-v1'):self.assertNotIn(value,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])
        self.assertIn('PG6334-current943-trace-v1',scope['report'].__code__.co_consts)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


class ActualOriginalCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts={name:(subject.PMO/name).read_text()for name in subject.NAMES}
        cls.head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=subject.ROOT,text=True).strip()
        saved=json.loads(cls.texts[subject.NAMES[2]])
        old='5eb040421ae9ea06ecc70c6eb2e152871c2d0d42'
        if saved['currentPhysicalCandidate']['source']!=old:
            prior=[r for r in saved['currentPhysicalCandidateHistory']if r['source']==old]
            if len(prior)!=1:raise ValueError('one preserved immutable before-candidate fixture')
            cls.head=prior[0]['metadataSource']
            cls.texts={name:subprocess.check_output(['git','show',cls.head+':documents/400_PGPT/470_PMO/'+name],cwd=subject.ROOT,text=True)for name in subject.NAMES}
        cls.proposed,cls.observed=subject.candidates(cls.texts,cls.head)
        cls.inventory=json.loads(cls.proposed[subject.NAMES[2]])

    def test_exact943_original4048_and_immutable_history_cost_acceptance(self):
        old=json.loads(self.texts[subject.NAMES[2]])
        self.assertEqual(old['artifacts'],self.inventory['artifacts'])
        self.assertEqual(old['measurementBindings'],self.inventory['measurementBindings'])
        self.assertEqual((943,4048,607,0),(self.observed['physicalArtifacts'],self.observed['tests'],self.observed['suites'],self.observed['acceptedLeafDelta']))
        self.assertEqual({'LINE':3554,'METHOD':687,'CLASS':38,'BRANCH':723},self.observed['remaining'])
        self.assertEqual(subject.SOURCE,self.inventory['currentPhysicalCandidate']['source'])
        for name in subject.NAMES[:2]:self.assertEqual(self.texts[name],self.proposed[name])
        before=json.loads(self.texts[subject.NAMES[3]]);after=json.loads(self.proposed[subject.NAMES[3]])
        for key in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate'):
            self.assertEqual(before[key],after[key])

    def test_wrong_bytes_missing_duplicate_acceptance_measurement_cost_rejected(self):
        changes=(lambda c:c['artifacts'].pop(),lambda c:c['artifacts'].append(copy.deepcopy(c['artifacts'][0])),
            lambda c:c['artifacts'][0].update(sha256='a'*64),lambda c:c.update(acceptedLeafDelta=1),
            lambda c:c['artifacts'][-1].update(additionalBudgetPp=1),
            lambda c:c['measurement'].update(sha256='b'*64),lambda c:c.update(effortPercent=100))
        for i,change in enumerate(changes):
            bad=copy.deepcopy(self.inventory);change(bad['currentPhysicalCandidate'])
            with self.subTest(vector=i),self.assertRaises(ValueError):subject.trace.verify_candidate(bad)


if __name__=='__main__':unittest.main()
