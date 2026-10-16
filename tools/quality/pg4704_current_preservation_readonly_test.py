"""Original read-only body unchanged; new output/data views, no old authority transfer."""
import ast
import unittest
from pyflakes.api import check
import pg4704_current_preservation_readonly as tool


class CurrentPreservation(unittest.TestCase):
    def test_complete_original_read_checks_retained_and_new_paths_only(self):
        original = ast.parse((tool.W / tool.ORIGINAL / 'payload.private.py').read_text())
        current = ast.parse(tool.payload())
        before = {n.name: ast.dump(n) for n in original.body if isinstance(n, ast.FunctionDef)}
        after = {n.name: ast.dump(n) for n in current.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual(before, after)
        # All executable assertions/capture before the result construction are identical.
        def prefix(tree):
            nodes = tree.body
            start = next(i for i,n in enumerate(nodes) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='HASHES'for t in n.targets))
            end = next(i for i,n in enumerate(nodes) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets))
            return [ast.dump(n)for n in nodes[start:end]]
        self.assertEqual(prefix(original), prefix(current))
        raw = tool.payload(); self.assertEqual(0, check(raw, '<fresh normal-current verifier>'))
        self.assertIn('runtimeConfigFilesToRetire=0',raw)
        for value in ['freshCurrentPreservation=True','dataOnlyNotRuntimeAuthority=True','nativeCandidateCredit=False',tool.AFTER_SHA]: self.assertIn(value,raw)
        self.assertIn("save = base / '"+tool.SLOT+"'",raw)


if __name__ == '__main__': unittest.main()
