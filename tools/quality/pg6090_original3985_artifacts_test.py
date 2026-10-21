import ast
import inspect
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6090_original3985_artifacts as p


class OriginalArtifactDefinitionTest(unittest.TestCase):
    def test_exact_old_fixture_suffixes_and_six_new_semantic_case_identities(self):
        # Historical declaration fixture is SOURCE, not today's expanded Test tree.
        original = Path.read_text
        inputs = {p.ROOT/name: subprocess.check_output(['git','show',p.SOURCE+':'+name],cwd=p.ROOT,text=True)
                  for name in set(p.TESTS)|{p.PROVIDER_TEST}}
        def archived(path,*args,**kwargs):
            return inputs[path] if path in inputs else original(path,*args,**kwargs)
        with patch.object(Path,'read_text',archived):
            rows = p.new_case_identities()
        self.assertEqual(6, len(rows))
        self.assertEqual(6, len(p.reader.expected_case_keys(rows)))
        self.assertEqual({'api', 'web'}, {r['module'] for r in rows})

    def test_complete_readonly_emitted_reader_has_explicit_campaign(self):
        raw = p.reader.emitted('0'*64, '/home/mini/schubert-nk-pgpt/transfer/PG6090-original3985-v1')
        ast.parse(raw)
        self.assertIn("('PG6088', (3985, 595, 1667), 5)", raw)
        self.assertIn("campaign not in ('PG6088', 'PG6118', 'PG6196', 'PG6212', 'PG6244', 'PG6272', 'PG6302', 'PG6330', 'PG6386', 'PG6408', 'PG6452')", raw)
        self.assertIn("coverage_artifacts[module]", raw)
        for value in ('mvn ', 'systemctl', 'qemu-system', 'sudo ', '--resume', '--recover'):
            self.assertNotIn(value, raw)

    def test_all_used_reader_exports_and_both_operator_namespaces_are_complete(self):
        for node in ast.walk(ast.parse(inspect.getsource(p))):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'reader':
                self.assertTrue(hasattr(p.reader, node.attr), node.attr)
        self.assertEqual(0, checkPath(p.__file__))
        self.assertEqual(0, checkPath(p.reader.__file__))


if __name__ == '__main__':
    unittest.main()
