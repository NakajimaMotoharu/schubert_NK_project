"""Exact historical941/17 plus current941; independent corrupt/foreign/omission vectors."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg4946_current_physical_trace as target
import wbs_candidate_trace as trace
import wbs_progress_audit as audit

BASE='5a0c2cbc920cddde110a3017c33023e6422be287'


class DualInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts={n:subprocess.check_output(['git','show',BASE+':documents/400_PGPT/470_PMO/'+n],cwd=target.ROOT,text=True)for n in target.NAMES}
        cls.proposed=target.candidates(cls.texts)
        cls.original=json.loads(cls.texts[target.NAMES[2]])
        cls.current=json.loads(cls.proposed[target.NAMES[2]])

    def test_historical_941_and_all_acceptance_cost_bytes_unchanged(self):
        self.assertEqual(self.original['artifacts'],self.current['artifacts'])
        self.assertEqual(self.original['measurementBindings'],self.current['measurementBindings'])
        self.assertEqual(self.original['source'],self.current['source'])
        old=json.loads(self.texts[target.NAMES[3]]);new=json.loads(self.proposed[target.NAMES[3]])
        for key in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate'):
            self.assertEqual(old[key],new[key],key)
        for n in target.NAMES[:2]:self.assertEqual(self.texts[n],self.proposed[n],n)
        current=trace.verify_candidate(self.current)
        self.assertEqual(941,current['physicalArtifacts']);self.assertEqual(2,current['relocations'])
        self.assertEqual(5,current['modulesFourCountersClosed'])
        self.assertEqual({'LINE':715,'METHOD':146,'CLASS':9,'BRANCH':442},current['remaining'])
        self.assertEqual(0,current['acceptedLeafDelta']);self.assertIsNone(current['effortPercent'])

    def test_actual_all_wbs_staged_audit_no_repository_mutation(self):
        with tempfile.TemporaryDirectory(prefix='pg4946-wbs-independent-')as directory:
            root=Path(directory)
            for n,text in self.proposed.items():(root/n).write_text(text)
            args=dict(master_path=root/target.NAMES[0],budget_path=root/target.NAMES[1],inventory_path=root/target.NAMES[2],snapshot_path=root/target.NAMES[3])
            result=audit.verify(**args)
            self.assertEqual((190,252,17),(result['wbsItems'],result['executionLeaves'],result['acceptedTasks']))
            self.assertFalse(result['formalAcceptanceChangedByAudit'])
            bad=json.loads(self.proposed[target.NAMES[3]]);bad['currentPhysicalCandidateMeasurement']['modulesFourCountersClosed']=6
            (root/target.NAMES[3]).write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'current candidate technical snapshot drift'):audit.verify(**args)

    def test_foreign_missing_duplicate_hash_owner_acceptance_and_scope_rejected(self):
        mutations=[lambda c:c.update(source=self.original['source']),
                   lambda c:c['artifacts'].pop(),lambda c:c['artifacts'].append(c['artifacts'][0]),
                   lambda c:c['artifacts'][0].update(sha256='a'*64),
                   lambda c:c['artifacts'][0].update(owner='WBS-N14'),
                   lambda c:c['artifacts'][0].update(costOwner='WBS-N14'),
                   lambda c:c['artifacts'][0].update(acceptance='ACCEPTED'),
                   lambda c:c.update(scopeChanged=True),lambda c:c.update(acceptedLeafDelta=1),
                   lambda c:c.update(historicalDescriptorSha256='a'*64),
                   lambda c:c.update(relocations={}),lambda c:c['design'].update(sha256='a'*64),
                   lambda c:c['measurement'].update(sha256='a'*64)]
        for i,mutate in enumerate(mutations):
            bad=copy.deepcopy(self.current);mutate(bad['currentPhysicalCandidate'])
            with self.subTest(vector=i),self.assertRaises(ValueError):trace.verify_candidate(bad)

    def test_current_worktree_corruption_not_hidden_by_historical_success(self):
        selected=self.current['currentPhysicalCandidate']['artifacts'][0];actual=trace.ROOT/selected['path']
        original=Path.read_bytes
        def read(path,*args,**kwargs):return b'corrupted current bytes'if path==actual else original(path,*args,**kwargs)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'current candidate physical byte mismatch'):
            trace.verify_candidate(self.current)
        for path in (target.__file__,trace.__file__,audit.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
