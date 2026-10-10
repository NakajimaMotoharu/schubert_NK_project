"""PT-DEP-1051001..002 new-slot/start-source trace guard; no VM operations."""
import ast
import unittest
from pathlib import Path
from pg1051_cold_tree_preflight_v2 import payload


class Trace(unittest.TestCase):
    def test_unique_fixed_labels_and_new_slot(self):
        raw=payload()
        self.assertEqual(2,raw.count('PG1051-cold-tree-preflight-v2'))
        self.assertNotIn('PG1050-cold-tree-preflight-v1',raw)
        self.assertIn("save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-prepared-v1/tree-preflight-v2')",raw)
        self.assertIn('assert not os.path.lexists(save)',raw)

    def test_start_source_is_captured_once_before_wait_and_log_is_persistent(self):
        raw=Path(__file__).with_name('pg1051_cold_tree_preflight_v2.py').read_text()
        tree=ast.parse(raw)
        heads=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)
               and n.func.attr=='check_output']
        self.assertEqual(1,len(heads))
        self.assertLess(raw.index("'operatorSource':source"),raw.index('actual = proc.wait()'))
        self.assertIn('result=dict(begin,actualExit=actual',raw)
        self.assertNotIn('timeout=',raw)
        self.assertIn("stdout=log,stderr=log",raw)


if __name__=='__main__':
    unittest.main()
