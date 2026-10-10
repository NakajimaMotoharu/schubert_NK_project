"""PT-DEP-1066001..002 independent lifetime/receipt/source guard."""
import ast
import unittest
from pg1066_cold_prepared_post_v2 import payload


class Post(unittest.TestCase):
    def test_metadata_refs_are_held_until_all_observations_then_reverse_close(self):
        raw=payload();ast.parse(raw)
        self.assertLess(raw.index('manager.RefUnit(name)'),raw.index("first=env['snapshot']()"))
        self.assertLess(raw.index("runtime=env['runtime_namespaces']()"),raw.index('manager.UnrefUnit(name)'))
        self.assertIn('for name in reversed(refs)',raw)
        self.assertLess(raw.index('bus.close()'),raw.index("'observerRefsNormalClose':True"))
        self.assertIn('while True:time.sleep(1)',raw)

    def test_independent_exact_receipt_bytes_and_fresh_label(self):
        raw=payload()
        self.assertIn("(save/'complete.private').read_bytes()",raw)
        self.assertIn("b'allScopesReturnedNormally=true\\nfinitePreparation=true\\nepochDbBusinessWrites=0\\n'",raw)
        self.assertNotIn('complete.private.txt',raw)
        self.assertNotIn('PG1065-cold-prepared-post-v1',raw)
        self.assertIn('first==second==before==after',raw)
        self.assertIn("runtime==env['runtime_namespaces']()==after['runtime']",raw)


if __name__=='__main__':
    unittest.main()
