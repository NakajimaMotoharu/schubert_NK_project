import ast
import inspect
import unittest
import pg6120_original3988_artifacts as subject
from pyflakes.api import check


class Definition(unittest.TestCase):
    def test_new_case_identities_and_reader_export_contract(self):
        added = subject.new_case_identities()
        self.assertEqual(3, len(added))
        self.assertEqual(3, len({r['caseNameSha256'] for r in added}))
        self.assertTrue(callable(subject.reader.production_source_inputs))
        self.assertTrue(callable(subject.reader.collect))
        source = inspect.getsource(subject.reader.inspect_original)
        ast.parse(source)
        emitted = subject.reader.emitted('0'*64, '/home/mini/schubert-nk-pgpt/transfer/PG6120-definition-only')
        self.assertEqual(0, check(emitted, '<complete original reader definition>'))
        self.assertIn("('PG6118', (3988, 595, 1667), 4)", source)
        self.assertIn("campaign not in ('PG6088', 'PG6118', 'PG6196', 'PG6212')", source)
        self.assertIn('expected_case_keys', source)


if __name__ == '__main__':
    unittest.main()
