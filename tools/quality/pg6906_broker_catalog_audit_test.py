import copy
import hashlib
import unittest
import pg6906_broker_catalog_audit as p


class BrokerCatalogAuditTest(unittest.TestCase):
    def test_scope_cannot_silently_remove_exit_dependency(self):
        row = dict(ownedArtifacts=[p.MAIN], sharedClassReferences=[], dependencies=['WBS-P002-03', 'WBS-C04'])
        p.check_scope(row)
        for key, value in (('dependencies', ['WBS-C04']), ('ownedArtifacts', []), ('sharedClassReferences', ['other'])):
            bad = copy.deepcopy(row)
            bad[key] = value
            with self.assertRaises(ValueError):
                p.check_scope(bad)

    def test_original_two_method_identity_required_not_vector_counts(self):
        text = (p.ROOT / p.TEST).read_text()
        cases = [dict(**{'class': p.CLASS}, caseNameSha256=hashlib.sha256(p.source_case_candidates(text, n)[0].encode()).hexdigest()) for n in p.METHODS]
        self.assertEqual(2, len(p.join_cases(text, cases)))
        for bad in ([], cases[:1], cases + cases[:1]):
            with self.assertRaises(ValueError):
                p.join_cases(text, bad)


if __name__ == '__main__':
    unittest.main()
