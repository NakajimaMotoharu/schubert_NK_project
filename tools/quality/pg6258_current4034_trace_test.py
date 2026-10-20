import copy
import json
import subprocess
import unittest
import pg6258_current4034_trace as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_fixed_current_measurement_definitions_not_old3985(self):
        scope=subject.definitions('a'*64,'b'*64)
        values=scope['measurement'].__code__.co_consts
        self.assertIn(4034,values);self.assertIn(606,values);self.assertIn('PG6244-six-v1',values)
        self.assertNotIn(3985,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])

    def test_host_only_no_acceptance_or_support_readdition(self):
        scope=subject.definitions('a'*64,'b'*64)
        self.assertIn('PG6258-current943-trace-v1',scope['report'].__code__.co_consts)
        self.assertEqual(0,checkPath(subject.__file__))
        self.assertEqual(0,checkPath(__file__))


class ActualOriginalCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts={name:(subject.PMO/name).read_text()for name in subject.NAMES}
        cls.head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=subject.ROOT,text=True).strip()
        cls.proposed,cls.observed=subject.candidates(cls.texts,cls.head)
        cls.inventory=json.loads(cls.proposed[subject.NAMES[2]])

    def test_exact943_current4034_and_immutable_historical_acceptance(self):
        old=json.loads(self.texts[subject.NAMES[2]])
        self.assertEqual(old['artifacts'],self.inventory['artifacts'])
        self.assertEqual(old['measurementBindings'],self.inventory['measurementBindings'])
        self.assertEqual((943,4034,606,0),(self.observed['physicalArtifacts'],self.observed['tests'],self.observed['suites'],self.observed['acceptedLeafDelta']))
        self.assertEqual({'LINE':3554,'METHOD':687,'CLASS':38,'BRANCH':723},self.observed['remaining'])
        self.assertEqual(2,self.inventory['currentPhysicalCandidate']['version'])
        for name in subject.NAMES[:2]:self.assertEqual(self.texts[name],self.proposed[name])
        before=json.loads(self.texts[subject.NAMES[3]]);after=json.loads(self.proposed[subject.NAMES[3]])
        for key in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate'):
            self.assertEqual(before[key],after[key])

    def test_wrong_bytes_missing_duplicate_acceptance_and_measurement_rejected(self):
        changes=(lambda c:c['artifacts'].pop(),lambda c:c['artifacts'].append(copy.deepcopy(c['artifacts'][0])),
            lambda c:c['artifacts'][0].update(sha256='a'*64),lambda c:c.update(acceptedLeafDelta=1),
            lambda c:c['artifacts'][-1].update(additionalBudgetPp=1),
            lambda c:c['measurement'].update(sha256='b'*64),lambda c:c.update(effortPercent=100))
        for i,change in enumerate(changes):
            bad=copy.deepcopy(self.inventory);change(bad['currentPhysicalCandidate'])
            with self.subTest(vector=i),self.assertRaises(ValueError):subject.trace.verify_candidate(bad)


if __name__=='__main__':unittest.main()
