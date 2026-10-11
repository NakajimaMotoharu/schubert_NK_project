"""Independent FLOCK inverse and unchanged fullscope; no OS signals."""
import ast
import os
from types import SimpleNamespace
import unittest
import pg1353_bootstrap_fixed_handoff as p

class Test(unittest.TestCase):
    def payload_tree(self):
        raw = p.payload(dict.fromkeys(p.prior.previous.prior.prior.previous.transport.previous.SEALS, 'b' * 64))
        return raw, ast.parse(raw)

    def test_same_all_protected_statements_except_owned_flock(self):
        raw, tree = self.payload_tree()
        functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        owned, free = functions['owned_snapshot'], functions['free_snapshot']
        self.assertEqual(len(owned.body), len(free.body))
        differences = [i for i, (a,b) in enumerate(zip(owned.body, free.body)) if ast.dump(a) != ast.dump(b)]
        self.assertEqual(1, len(differences))
        self.assertIn('maintenance.lock', ast.unparse(owned.body[differences[0]]))
        self.assertNotIn("owner['pid']", ast.unparse(free))
        self.assertIn('terminate_once(838452,7697543', raw)
        self.assertIn('oldNormalClose', raw)
        self.assertIn('signals==1', raw)

    def test_actual_generated_free_inode_guard(self):
        _, tree = self.payload_tree()
        free = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'free_snapshot')
        guard = next(n for n in ast.walk(free) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name) and n.func.id == 'require'
                     and n.args and isinstance(n.args[0], ast.UnaryOp)
                     and 's.st_ino' in ast.unparse(n.args[0]))
        expression = compile(ast.Expression(body=guard.args[0]), '<actual free inode guard>', 'eval')
        st = SimpleNamespace(st_dev=os.makedev(0,28), st_ino=1996)
        self.assertFalse(eval(expression, {'os': os, 's': st, 'd':['00','1c','1996']}))
        for value in (['00','1c','1997'], ['00','1d','1996']):
            self.assertTrue(eval(expression, {'os':os,'s':st,'d':value}))

if __name__ == '__main__':
    unittest.main()
