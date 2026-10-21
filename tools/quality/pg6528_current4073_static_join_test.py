"""Current XML identity rebinding; no Main or dynamic PT operations."""
import copy
import unittest
import pg6528_current4073_static_join as subject


class RebindTest(unittest.TestCase):
    def fixture(self):
        case = dict(testId='current', xmlSha256='new-xml', **{'class': 'C'},
                    caseNameSha256='name', source=subject.SOURCE, result='PASS_ORIGINAL_XML')
        rows = [dict(status='REQUIRED_CONTRACT', currentWholeCaseRefs=[dict(case, source=subject.OLD)]),
                dict(status='CONTEXT_NOT_APPLICABLE', staticContextPremiseOnly=True),
                dict(status='NOT_REVIEWED_CURRENT_SOURCE', reason='held')]
        return rows, [case]

    def test_rebinds_only_current_refs_and_retains_hold_and_input(self):
        rows, cases = self.fixture(); before = copy.deepcopy(rows)
        result, counts = subject.rebind(rows, cases, subject.SOURCE)
        self.assertEqual(before, rows)
        self.assertEqual(rows[2], result[2])
        self.assertEqual(subject.SOURCE, result[0]['currentWholeCaseRefs'][0]['source'])
        self.assertEqual('new-xml', result[0]['currentWholeCaseRefs'][0]['xmlSha256'])
        self.assertEqual({'actualCurrentCaseRefs': 1, 'staticContextOnly': 1}, counts)

    def test_missing_duplicate_old_or_failed_case_cannot_be_success(self):
        rows, cases = self.fixture()
        without_result = {k:v for k,v in cases[0].items() if k != 'result'}
        for bad in ([], cases+cases, [dict(cases[0], source=subject.OLD)],
                    [dict(cases[0], result='FAILED')], [without_result]):
            with self.assertRaises(ValueError):
                subject.rebind(rows, bad, subject.SOURCE)
        with self.assertRaises(ValueError):
            subject.rebind([dict(status='REQUIRED_CONTRACT')], cases, subject.SOURCE)


if __name__ == '__main__':
    unittest.main()
