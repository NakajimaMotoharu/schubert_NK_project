import unittest
from pyflakes.api import check
import pg5934_static3973_join as t


class Current545JoinDefinitionTest(unittest.TestCase):
    def test_same_source_receipt_and_new_case_reference_schema(self):
        raw = t.qualification_source()+'\n'+t.reader_source()
        self.assertIn('PG5926-current3973-cases', raw)
        self.assertIn('pg5928-api-storage-qualified-v1', raw)
        self.assertIn('(545, 239, 1544)', raw)
        scope = {**vars(t.previous), 'SOURCE': t.SOURCE, 'PENDING': None, 'PENDING_SHA': None}
        prefix = '\n'.join(n+'=None' for n in scope if n.isidentifier() and not n.startswith('__') and n not in ('main', 'qualified_whole'))+'\n'
        self.assertEqual(0, check(prefix+raw, '<complete545 join namespace>'))
        reference = {'class': 'fixture', 'caseNameSha256': 'a'*64, 'selectedMethod': 'case', 'historicalIdentityOnly': True}
        current = {'testId': 'actual', 'class': 'fixture', 'caseNameSha256': 'a'*64, 'xmlSha256': 'b'*64, 'result': 'PASS_ORIGINAL_XML'}
        value = t.previous.current_reference(reference, {('fixture', 'a'*64): [current]})
        self.assertEqual('actual', value['testId'])
        with self.assertRaises(ValueError):
            t.previous.current_reference(reference, {('fixture', 'a'*64): [dict(current, result='UNKNOWN')]})


if __name__ == '__main__':
    unittest.main()
