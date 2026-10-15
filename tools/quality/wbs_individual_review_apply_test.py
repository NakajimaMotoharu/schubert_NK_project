import copy
import hashlib
import tempfile
from pathlib import Path
import unittest
from wbs_individual_review_apply import reviewed_acceptance


class ExplicitReviewTest(unittest.TestCase):
    def test_all_criteria_exact_source_scope_evidence_and_negative_contracts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'proof').write_text('independent literal evidence')
            sha = hashlib.sha256((root / 'proof').read_bytes()).hexdigest()
            task = {'id': 'A', 'acceptance': {'status': 'NOT_ACCEPTED'}, 'acceptanceChecks': [{'id': 'A:contract'}, {'id': 'A:quality'}], 'ownedArtifacts': ['one'], 'requirementIds': ['R001']}
            review = {'wbs': 'A', 'productionSource': 'S', 'criteriaSatisfied': ['A:contract', 'A:quality'], 'reviewedBy': 'explicit review', 'run': 'R', 'scopePaths': ['one'], 'requirementIds': ['R001'], 'expectedGeneratedFromProduction': False, 'evidence': [{'path': 'proof', 'sha256': sha, 'source': 'S', 'run': 'R', 'verifiedChecks': ['A:contract', 'A:quality']}]}
            self.assertEqual('ACCEPTED', reviewed_acceptance(review, task, 'S', root)['status'])
            for key, value in [('productionSource', 'foreign'), ('criteriaSatisfied', ['A:contract']), ('scopePaths', []), ('requirementIds', []), ('expectedGeneratedFromProduction', True), ('reviewedBy', '')]:
                bad = copy.deepcopy(review); bad[key] = value
                with self.subTest(key=key), self.assertRaises(ValueError):
                    reviewed_acceptance(bad, task, 'S', root)
            for key, value in [('sha256', '0' * 64), ('source', 'foreign'), ('path', '../proof'), ('verifiedChecks', ['A:contract']), ('run', '')]:
                bad = copy.deepcopy(review); bad['evidence'][0][key] = value
                with self.subTest(evidence=key), self.assertRaises(ValueError):
                    reviewed_acceptance(bad, task, 'S', root)
            task['acceptance']['status'] = 'ACCEPTED'
            with self.assertRaises(ValueError):
                reviewed_acceptance(review, task, 'S', root)


if __name__ == '__main__':
    unittest.main()
