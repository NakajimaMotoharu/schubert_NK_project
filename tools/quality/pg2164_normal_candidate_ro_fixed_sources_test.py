import ast
import unittest
from pg2164_normal_candidate_ro_fixed_sources import sources


class Roles(unittest.TestCase):
    def test_independent_whole_graph_candidate_current_matrix(self):
        v=sources('a'*64);raw='\n'.join(v.values())
        self.assertNotIn('0.1.0-PG1638',raw)
        self.assertIn("candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126')",v['pg2164_native_refs.py'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG1846',v['Pg2164CandidateRo.java'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2126',v['pg2164_input_preflight.py'])
        self.assertIn('genuineParentNormalWarningOriginal=true',raw)
        self.assertIn("'SuccessExitStatus': '10'",raw)
        for body in v.values():
            self.assertNotIn('pg2152-normal-candidate-ro-tools-v1',body)
        # Extract every actual candidate_root assignment, not an import-only stub.
        roots=[]
        for name,body in v.items():
            if name.endswith('.py'):
                for n in ast.walk(ast.parse(body)):
                    if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='candidate_root'for t in n.targets):roots.append(ast.literal_eval(n.value.args[0]))
        self.assertEqual(roots,['/opt/schubert-nk/releases/0.1.0-PG2126'])


if __name__=='__main__':unittest.main()
