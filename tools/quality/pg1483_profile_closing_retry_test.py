import ast
import unittest
from pg1483_profile_closing_retry import payload


class ClosingBindingTest(unittest.TestCase):
    def test_binding_before_use_and_one_diagnostic_pop_no_profile_rerun(self):
        source=payload();x=ast.parse(source)
        root=next(i for i,n in enumerate(x.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROOT'for t in n.targets))
        use=next(i for i,n in enumerate(x.body)if isinstance(n,ast.For)and 'profile_after' in ast.unparse(n))
        self.assertLess(root,use)
        self.assertEqual("ROOT = pathlib.Path('/run/schubert-nk')",ast.unparse(x.body[root]))
        self.assertEqual(1,source.count("first['brokerActor'].pop('statusSha256')"))
        self.assertIn('first==second==profile_after',source)
        for text in ['pg1482-partial-profile-closing-v1','systemctl\',\'stop','Pg1478PartialOriginalProfile\',\'profile']:
            self.assertNotIn(text,source)
        self.assertIn("'stopRevokeRetirementIssued':False",source)


if __name__=='__main__':unittest.main()
