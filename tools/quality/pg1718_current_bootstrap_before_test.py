"""Independent readonly baseline closure and no static execution-history oracle."""
import ast
import unittest
from pg1718_current_bootstrap_before import payload


class BeforeTest(unittest.TestCase):
    def test_whole_current_source_and_ref_scope_are_required(self):
        raw=payload();tree=ast.parse(raw)
        for expected in ['2741c4546afad6c1e8b6efbd53dfb58144edf7bb',
                         'pg1703_parent_receipt.py','pg1718-current-bootstrap-before-v1',
                         "users[0]['role']=='ADMIN'",'bootstrap-admin-username','bootstrap-admin-password']:
            self.assertIn(expected,raw)
        self.assertNotIn('StartUnit',raw);self.assertNotIn('StopUnit',raw)
        self.assertNotIn('len(value[\'rows\'][\'schubert.batch_runs\'])==594',raw)
        scope=next(n for n in tree.body if isinstance(n,ast.Try))
        self.assertIn('UnrefUnit',ast.unparse(ast.Module(body=scope.finalbody,type_ignores=[])))


if __name__=='__main__':unittest.main()
