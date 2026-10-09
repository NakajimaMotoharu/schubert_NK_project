"""Independent literal reactor/recipe regression for BUG925, no Maven/VM operation."""
import ast
import unittest
from pathlib import Path
import pg744_closing_selected as candidate


class ReactorTest(unittest.TestCase):
    def test_explicit_leafs_and_new_slot_without_aggregator_or_am(self):
        raw = candidate.source()
        tree = ast.parse(raw)
        command = next(node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'command' for t in node.targets))
        values = [node.value for node in command.elts if isinstance(node, ast.Constant)]
        self.assertNotIn('-am', values)
        self.assertEqual('src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api', values[values.index('-pl')+1])
        for goal in ('spotless:check','test-compile','test','spotbugs:check','jacoco:report','jar:jar'):
            self.assertIn(goal, values)
        self.assertNotIn('-DskipTests', values)
        self.assertIn("D = W / 'pg744-closing-selected-v1'", raw)
        self.assertIn("with (D / 'exit').open('x')", raw)
        self.assertIn("subprocess.check_output(['git', 'status', '--porcelain']", raw)
        old = Path(candidate.R / 'pg743_closing_selected.py').read_text()
        self.assertIn("'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',", old)
        self.assertIn("D = W / 'pg743-closing-selected-v1'", old)


if __name__ == '__main__': unittest.main()
