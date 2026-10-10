import ast
import unittest
from pg1300_current_candidate_ro_sources import sources


class CurrentCandidateReadOnlyTest(unittest.TestCase):
    def test_current_ordinary_done_not_cold_and_no_replacement(self):
        files=sources();java=files['Pg1300CandidateRo.java'];refs=files['pg1300_native_refs.py']
        for n,s in files.items():
            if n.endswith('.py'):ast.parse(s)
        self.assertIn('State.ISSUED',java)
        self.assertIn('candidateReadOnly();refs.check("ro")',java)
        self.assertIn('if(!readOnlyMount(mounts,target))',java)
        self.assertIn('PG1292',java)
        self.assertNotIn('def place_candidate',refs)
        self.assertNotIn('tar.extractall',refs)
        self.assertNotIn('refs.check("place")',java)
        self.assertIn('candidate_ro_post(candidate_before)',refs)
        self.assertIn('PG998-native-stage',refs)
        helper=files['pg1300_native_owned_stop.py'];env={}
        tree=ast.parse(helper);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'require','placement_family','placement_action'}]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<real ro boundary>','exec'),env)
        self.assertTrue(env['placement_family']([b'/opt/jdk-25.0.4/bin/java',b'-cp',b'fixed',b'Pg1300CandidateRo',b'prepare-ro',b'']))
        self.assertFalse(env['placement_family']([b'/opt/jdk-25.0.4/bin/java',b'-cp',b'fixed',b'Pg1300CandidateRo',b'place',b'']))
        self.assertTrue(env['placement_action']('ro',False))
        for action in ['place','stop','activate']:
            with self.assertRaises(ValueError):env['placement_action'](action,False)


if __name__=='__main__':unittest.main()
