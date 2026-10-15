"""Actual final composed reader roles and nested independent oracle boundaries, no VM."""
import ast
import unittest
from pyflakes.api import check
import pg3582_current_browser_acceptance as root
import pg3592_current_browser_composite_seal as composite


class Composite(unittest.TestCase):
    def test_actual_outer_new_save_and_existing_prefix(self):
        live=root.live();binding={**live['binding'],'rootPid':live['rootPid']}
        original=root.seal_payload(binding)
        raw=composite.compose(original,{'before':{},'after':{},'context':{}},'b'*64)
        self.assertEqual(0,check(raw,'<whole actual current composite>'))
        ns={n.targets[0].id:n.value for n in ast.parse(raw).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
        self.assertIn(composite.SLOT,ast.unparse(ns['SAVE']))
        oracle=ast.literal_eval(ns['ORACLE'])
        self.assertIn('/'+root.SEAL+'/before.private.json',oracle)
        self.assertIn(root.SOURCE,oracle)
        self.assertIn(root.BOM,oracle)
        self.assertIn("require(new==CHAIN['after'])",oracle)
        self.assertIn('ROOT_ORACLE=',oracle)
        self.assertIn('BROWSER_ORACLE=',oracle)
        self.assertIn('PARTIAL_CHAIN=[]',oracle)
        # Independent source rebinding is limited to the added nested oracle;
        # the complete already-qualified terminal guard remains byte-identical.
        old_guard=next(ast.literal_eval(n.value)for n in ast.parse(original).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GUARD'for t in n.targets))
        self.assertEqual(old_guard,ast.literal_eval(ns['GUARD']))


if __name__=='__main__':unittest.main()
