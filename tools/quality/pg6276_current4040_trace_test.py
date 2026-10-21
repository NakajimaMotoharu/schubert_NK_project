import unittest
import copy
import json
import subprocess
import pg6276_current4040_trace as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_exact4040_run_and_no_old_measurement_values(self):
        scope=subject.definitions('a'*64,'b'*64);values=scope['measurement'].__code__.co_consts
        for value in (4040,607,'PG6272-six-v1'):self.assertIn(value,values)
        for value in (3985,4034,606,'PG6244-six-v1'):self.assertNotIn(value,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])

    def test_host_only_zero_new_supports_and_clean_definitions(self):
        scope=subject.definitions('a'*64,'b'*64)
        self.assertIn('PG6276-current943-trace-v1',scope['report'].__code__.co_consts)
        self.assertEqual(0,checkPath(subject.__file__))
        self.assertEqual(0,checkPath(__file__))


class ActualOriginalCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts={name:(subject.PMO/name).read_text()for name in subject.NAMES}
        cls.head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=subject.ROOT,text=True).strip()
        saved=json.loads(cls.texts[subject.NAMES[2]])
        if saved['currentPhysicalCandidate']['source']!='97dd2ba6185143632439f32dfc1d663061f1e55c':
            prior=[r for r in saved['currentPhysicalCandidateHistory']if r['source']=='97dd2ba6185143632439f32dfc1d663061f1e55c']
            if len(prior)!=1:raise ValueError('one preserved original before-candidate fixture')
            cls.head=prior[0]['metadataSource']
            cls.texts={name:subprocess.check_output(['git','show',cls.head+':documents/400_PGPT/470_PMO/'+name],cwd=subject.ROOT,text=True)for name in subject.NAMES}
        cls.proposed,cls.observed=subject.candidates(cls.texts,cls.head)
        cls.inventory=json.loads(cls.proposed[subject.NAMES[2]])

    def test_exact943_original4040_and_immutable_historical_fields(self):
        old=json.loads(self.texts[subject.NAMES[2]])
        self.assertEqual(old['artifacts'],self.inventory['artifacts'])
        self.assertEqual(old['measurementBindings'],self.inventory['measurementBindings'])
        self.assertEqual((943,4040,607,0),(self.observed['physicalArtifacts'],self.observed['tests'],self.observed['suites'],self.observed['acceptedLeafDelta']))
        self.assertEqual({'LINE':3554,'METHOD':687,'CLASS':38,'BRANCH':723},self.observed['remaining'])
        self.assertEqual(2,self.inventory['currentPhysicalCandidate']['version'])
        for name in subject.NAMES[:2]:self.assertEqual(self.texts[name],self.proposed[name])
        before=json.loads(self.texts[subject.NAMES[3]]);after=json.loads(self.proposed[subject.NAMES[3]])
        for key in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate'):
            self.assertEqual(before[key],after[key])

    def test_wrong_bytes_missing_duplicate_acceptance_measurement_and_cost_rejected(self):
        changes=(lambda c:c['artifacts'].pop(),lambda c:c['artifacts'].append(copy.deepcopy(c['artifacts'][0])),
            lambda c:c['artifacts'][0].update(sha256='a'*64),lambda c:c.update(acceptedLeafDelta=1),
            lambda c:c['artifacts'][-1].update(additionalBudgetPp=1),
            lambda c:c['measurement'].update(sha256='b'*64),lambda c:c.update(effortPercent=100))
        for i,change in enumerate(changes):
            bad=copy.deepcopy(self.inventory);change(bad['currentPhysicalCandidate'])
            with self.subTest(vector=i),self.assertRaises(ValueError):subject.trace.verify_candidate(bad)


if __name__=='__main__':unittest.main()
