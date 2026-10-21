import inspect
import unittest
from pyflakes.api import check
import pg6198_original4024_artifacts as subject


class Definition(unittest.TestCase):
    def test_actual_new36_source_identities_no_pass_results(self):
        rows=subject.new_case_identities(subject.original_source())
        self.assertEqual(36,len(rows))
        self.assertTrue(all(set(r)=={'module','class','caseNameSha256'} for r in rows))
        self.assertEqual(36,len(subject.reader.expected_case_keys(rows)))

    def test_reader_exact_new_campaign_and_coverage_not_replay(self):
        raw=inspect.getsource(subject.reader.inspect_original)
        self.assertIn("('PG6196', (4024, 605, 1667), 13)",raw)
        emitted=subject.reader.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6198-definition-only')
        self.assertEqual(0,check(emitted,'<original4024 read-only reader>'))
        self.assertIn("campaign not in ('PG6088', 'PG6118', 'PG6196', 'PG6212', 'PG6244', 'PG6272', 'PG6302', 'PG6330', 'PG6386', 'PG6408')",emitted)
        self.assertIn('expected_case_keys(actual)',emitted)


if __name__=='__main__':unittest.main()
