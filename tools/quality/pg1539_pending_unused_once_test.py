"""Exact framing/source admission; client0 alone never means scopes returned."""
import ast
import unittest
from pg1539_pending_unused_once import valid_receipt, source

class OnceTest(unittest.TestCase):
    def test_literal_framing(self):
        literal=b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1539_DONE unusedPlacement=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'
        self.assertTrue(valid_receipt(literal))
        for v in [None,literal.decode(),literal[:-1],literal+b'extra\n',literal.replace(b'unusedPlacement=true',b'readonlyProfile=true'),literal.replace(b'allScopesReturnedNormally=true',b'allScopesReturnedNormally=false')]:self.assertFalse(valid_receipt(v))

    def test_same_failed_original_frozen_path_and_one_place(self):
        s=source();ast.parse(s)
        args=next(n.value for n in ast.walk(ast.parse(s))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='args'for t in n.targets))
        self.assertEqual(ast.literal_eval(args.right)[-2:],['Pg1536PendingUnusedPlacement','place'])
        self.assertIn('pg1537-pending-unused-frozen-v1.safe.json',s)
        self.assertIn('success=result.returncode==0 and valid_receipt(log)',s)
        self.assertIn('out.mkdir(mode=0o700)',s)
        self.assertNotIn('StartUnit',s);self.assertNotIn('daemon-reload',s)

if __name__=='__main__':unittest.main()
