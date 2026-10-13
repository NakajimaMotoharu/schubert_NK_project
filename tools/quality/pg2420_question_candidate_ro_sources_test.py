import ast
import unittest
from pg2420_question_candidate_ro_sources import sources


class Roles(unittest.TestCase):
    def test_actual_all_current_candidate_roles_and_current_parent(self):
        values=sources('a'*64);whole='\n'.join(values.values())
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2406',values['pg2420_input_preflight.py'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2126',values['Pg2420CandidateRo.java'])
        self.assertIn('e1429ac8-f3dd-4e8c-83d2-1926c4ba8440',values['pg2420_parent_receipt.py'])
        self.assertIn('genuineParentNormalWarningOriginal=true',whole)
        roots=[]
        for name,body in values.items():
            self.assertNotIn('pg2164-normal-candidate-ro-tools-v1',body)
            if name.endswith('.py'):
                for n in ast.walk(ast.parse(body)):
                    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='candidate_root' for t in n.targets):
                        roots.append(ast.literal_eval(n.value.args[0]))
        self.assertEqual(['/opt/schubert-nk/releases/0.1.0-PG2406'],roots)
        for bom in [None,'x'*64,'a'*63]:
            with self.assertRaises(ValueError):
                sources(bom)


if __name__=='__main__':
    unittest.main()
