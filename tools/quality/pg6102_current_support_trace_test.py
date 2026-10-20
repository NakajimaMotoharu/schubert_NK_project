import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from pyflakes.api import checkPath
import pg6102_current_support_trace as p


class SupportDeclarationTest(unittest.TestCase):
    def candidate(self):
        artifacts=[]
        for path,(owner,origin) in p.trace.SUPPORT.items():
            artifacts.append(dict(path=path,historicalPath=None,kind='JAVA',owner=owner,costOwner=owner,
                implementationSupportOnly=True,supportingExistingLeaf=owner,originCommit=origin,additionalBudgetPp=0))
        return dict(version=2,logicalScopeChanged=False,physicalScopeDelta=dict(addedSupport=sorted(p.trace.SUPPORT),removed=[]),artifacts=artifacts)

    def test_exact_named_supports_and_existing_owner_only(self):
        old=[dict(owner='WBS-P005-03',costOwner='WBS-P005-03')]
        self.assertEqual(set(p.trace.SUPPORT),p.trace.support_declarations(self.candidate(),old))
        bads=[]
        for field,value in (('owner','WBS-P005-04'),('costOwner','WBS-P005-04'),('originCommit','a'*40),
                            ('additionalBudgetPp',1),('additionalBudgetPp',False),('historicalPath','invented'),('implementationSupportOnly',False)):
            candidate=self.candidate();candidate['artifacts'][0][field]=value;bads.append(candidate)
        candidate=self.candidate();candidate['artifacts'].pop();bads.append(candidate)
        candidate=self.candidate();candidate['logicalScopeChanged']=True;bads.append(candidate)
        for candidate in bads:
            with self.assertRaises(ValueError):p.trace.support_declarations(candidate,old)
        with self.assertRaises(ValueError):p.trace.support_declarations(self.candidate(),[])


class Current943CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts={n:(p.PMO/n).read_text() for n in p.NAMES}
        cls.head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p.ROOT,text=True).strip()
        cls.proposed,cls.observed=p.candidates(cls.texts,cls.head)
        cls.inventory=json.loads(cls.proposed[p.NAMES[2]])

    def test_exact943_host_only_and_history_not_promoted(self):
        before=json.loads(self.texts[p.NAMES[2]]);after=self.inventory
        self.assertEqual(before['artifacts'],after['artifacts'])
        self.assertEqual(before['measurementBindings'],after['measurementBindings'])
        self.assertEqual((943,2,0),(self.observed['physicalArtifacts'],self.observed['implementationSupportAdditions'],self.observed['acceptedLeafDelta']))
        self.assertEqual(3985,self.observed['tests']);self.assertFalse(self.observed['nativeQualified'])
        self.assertEqual(2,self.observed['modulesFourCountersClosed'])
        self.assertEqual({'LINE':3525,'METHOD':668,'CLASS':38,'BRANCH':722},self.observed['remaining'])
        for n in p.NAMES[:2]:self.assertEqual(self.texts[n],self.proposed[n])
        before=json.loads(self.texts[p.NAMES[3]]);after=json.loads(self.proposed[p.NAMES[3]])
        for key in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate'):
            self.assertEqual(before[key],after[key])

    def test_all_wbs_candidate_audit_and_negative_physical_vectors(self):
        with tempfile.TemporaryDirectory(prefix='pg6102-trace-audit-') as directory:
            root=Path(directory)
            for n,text in self.proposed.items():(root/n).write_text(text)
            result=p.audit.verify(master_path=root/p.NAMES[0],budget_path=root/p.NAMES[1],inventory_path=root/p.NAMES[2],snapshot_path=root/p.NAMES[3])
            self.assertEqual((190,252,17),(result['wbsItems'],result['executionLeaves'],result['acceptedTasks']))
            self.assertFalse(result['formalAcceptanceChangedByAudit'])
        mutations=[lambda c:c['artifacts'].pop(),lambda c:c['artifacts'].append(copy.deepcopy(c['artifacts'][0])),
                   lambda c:c['artifacts'][0].update(sha256='a'*64),lambda c:c.update(acceptedLeafDelta=1),
                   lambda c:c['artifacts'][-1].update(acceptance='ACCEPTED'),lambda c:c['artifacts'][-1].update(module='web'),
                   lambda c:c.update(physicalScopeDelta={'addedSupport':[],'removed':[]}),
                   lambda c:c['measurement'].update(sha256='b'*64)]
        for i,mutate in enumerate(mutations):
            bad=copy.deepcopy(self.inventory);mutate(bad['currentPhysicalCandidate'])
            with self.subTest(vector=i),self.assertRaises(ValueError):p.trace.verify_candidate(bad)
        for path in (p.__file__,p.trace.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__ == '__main__':
    unittest.main()
