"""Independent whole-generated command contract; never changes Production expected values."""
import ast
import unittest
from pyflakes.api import check
from pg2114_caddy_metadata_selected_v2 import server

class CommandContract(unittest.TestCase):
    def test_explicit_modules_without_parent_reactor(self):
        raw=server()
        self.assertEqual(0,check('HEAD="fixed"\nARCHIVE_SHA="fixed"\n'+raw,'<actual selected server>'))
        tree=ast.parse(raw)
        args=next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='args'for t in n.targets))
        literals=[n.value for n in args.elts if isinstance(n,ast.Constant)]
        self.assertNotIn('-am',literals)
        self.assertIn('-o',literals)
        self.assertIn('jar:test-jar',literals)
        self.assertIn('spotbugs:check',literals)
        modules=next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='modules'for t in n.targets))
        self.assertEqual(['protocol','storage','bootstrap','batch'],ast.literal_eval(modules))
        self.assertIn("'source-selected-PG2114'",raw)
        self.assertNotIn('PG2112',raw)

if __name__=='__main__':unittest.main()
