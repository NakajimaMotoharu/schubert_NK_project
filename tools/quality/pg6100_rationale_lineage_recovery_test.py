import unittest
from pg6100_rationale_lineage_recovery import recover, reason_of
from pg5918_api_static_rebind import prior_disposition


class ReasonLineageTest(unittest.TestCase):
    def test_exact_parent_only_and_no_pt_invention(self):
        row = dict(status='REQUIRED_CONTRACT', sourcePath='p', sourceSha256='source', reason='', priorFindingId='old', priorReviewManifestSha256='manifest')
        parent = {**row, 'findingId': 'old', 'priorReason': 'independent original rationale'}
        why, hops = recover(row, lambda digest, ident: (parent, {'reviewSource': 'oldSource'}))
        self.assertEqual('independent original rationale', why)
        self.assertEqual(1, len(hops))
        self.assertIsNone(reason_of({'reason': '\n', 'priorReason': []}))

    def test_source_change_classification_change_and_cycles_are_unresolved(self):
        row = dict(status='REQUIRED_CONTRACT', sourcePath='p', sourceSha256='source', reason='', priorFindingId='old', priorReviewManifestSha256='manifest')
        for parent in ({**row, 'sourceSha256': 'different', 'reason': 'cannot inherit'},
                       {**row, 'status': 'FALSE_POSITIVE', 'reason': 'different disposition'}, row):
            with self.assertRaises(ValueError):
                recover(row, lambda digest, ident: (parent, {}))

    def test_pending_and_decided_status_keep_reason_and_fallback(self):
        for status in ('SOURCE_REBOUND_CURRENT_WHOLE_PENDING','REQUIRED_CONTRACT'):
            row=dict(status=status,priorDisposition='REQUIRED_CONTRACT',priorReason='independent reason')
            value=prior_disposition(row)
            self.assertEqual('REQUIRED_CONTRACT',value['status'])
            self.assertEqual('independent reason',value['reason'])
            self.assertEqual(value['reason'],value['priorReason'])
            self.assertNotIn('reason',row)
        with self.assertRaises(ValueError):
            prior_disposition(dict(status='REQUIRED_CONTRACT',reason='',priorReason=' '))


if __name__ == '__main__':
    unittest.main()
