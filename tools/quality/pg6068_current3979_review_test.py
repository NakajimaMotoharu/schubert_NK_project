import hashlib
import unittest
import pg6068_current3979_review as t


class CurrentSourceReferencesTest(unittest.TestCase):
    def test_real_immutable_current3979_join_computation_without_publishing_or_pt(self):
        rows, proof = t.reviewed_result()
        self.assertEqual((1305, 631, False), (len(rows), proof['sourceAndWholeJoinedDispositions'], proof['formalAccepted']))
        self.assertEqual(674, proof['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])

    def test_selected_method_must_join_one_actual_current_source_identity(self):
        selected = {'className': 'Fixture', 'method': 'independent'}
        bare = hashlib.sha256(b'independent').hexdigest()
        parenthesized = hashlib.sha256(b'independent()').hexdigest()
        row = dict(**{'class': 'Fixture'}, caseNameSha256=bare, source=t.SOURCE,
                   result='PASS_ORIGINAL_XML', testId='new', xmlSha256='a'*64)
        self.assertEqual('new', t.selected_refs([selected], {('Fixture', bare): row})[0]['testId'])
        for wrong in ({}, {('Fixture', bare): dict(row, source=t.OLD)},
            {('Fixture', bare): row, ('Fixture', parenthesized): dict(row, caseNameSha256=parenthesized)}):
            with self.assertRaises(ValueError):
                t.selected_refs([selected], wrong)

    def test_old_ref_is_a_semantic_key_not_permission_to_import_old_pass(self):
        ref = dict(**{'class': 'Fixture'}, caseNameSha256='b'*64)
        row = dict(ref, source=t.SOURCE, result='PASS_ORIGINAL_XML', testId='actual', xmlSha256='c'*64)
        self.assertEqual('actual', t.current_refs([ref], {('Fixture', 'b'*64): row}, source=t.SOURCE)[0]['testId'])
        with self.assertRaises(ValueError):
            t.current_refs([ref], {('Fixture', 'b'*64): dict(row, source=t.OLD)}, source=t.SOURCE)


if __name__ == '__main__':
    unittest.main()
