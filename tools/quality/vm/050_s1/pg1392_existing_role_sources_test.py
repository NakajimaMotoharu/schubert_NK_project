"""Actual generated protocol matrix and whole no-mutation existing-role join."""
import ast
import unittest
import pg1392_existing_role_sources as p

class Test(unittest.TestCase):
    def test_actual_phase_action_matrix(self):
        raw=p.files()['pg1392_bootstrap_role_refs.py'];tree=ast.parse(raw)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='expected_presence')
        env={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual sent phase contract>','exec'),env)
        f=env['expected_presence'];gold={('READY',b'before'):True,('BEFORE',b'prepared'):True,('PREPARED',b'closed'):False,('CLOSED',b'release'):False}
        for state in ('READY','BEFORE','PREPARED','CLOSED'):
            for action in (b'before',b'prepared',b'closed',b'release'):
                if (state,action)in gold:self.assertIs(gold[(state,action)],f(state,action))
                else:
                    with self.assertRaises(ValueError):f(state,action)
        for state,action in ((None,b'closed'),('PREPARED',None),('PREPARED','closed'),(True,b'closed'),('UNKNOWN',b'closed'),('CLOSED',b'unknown')):
            with self.assertRaises(ValueError):f(state,action)
        self.assertIn('holder(expected_presence(state,action))',raw)
        self.assertNotIn("holder(state!='CLOSED')",raw)

    def test_whole_existing_role_no_recreate(self):
        values=p.files();joined='\n'.join(values.values())
        self.assertIn('common.openExistingChild("ordinary-bootstrap196")',joined)
        self.assertNotIn('Pg1370BootstrapRoleDirectory.prepare',joined)
        self.assertNotIn('policy.delta(prior,now',joined)
        self.assertIn('require(now==prior)',joined)
        self.assertIn(p.BASE,joined);self.assertIn(p.BASE_SHA,joined)
        self.assertIn('PG998-bootstrap-role',joined)
        self.assertIn('oneBootstrapRoleVerified=true',joined)
        self.assertNotIn('pg1344-current-bootstrap-before-v1',joined)

if __name__=='__main__':unittest.main()
