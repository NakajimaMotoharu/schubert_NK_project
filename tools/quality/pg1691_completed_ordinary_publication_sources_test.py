"""Independent fixed old/new/cohort vectors, no mutating execution."""
import ast
import unittest
from pyflakes.api import check
import pg1691_completed_ordinary_publication_sources as p
import pg1693_completed_publication_compile as compiler


class OrdinarySourceTest(unittest.TestCase):
    def test_current_candidate_and_complete_cohort_are_role_bound(self):
        s=p.sources();java=s['Pg1691OrdinaryPublication.java'];oracle=s['pg1691_ordinary_publication_contract.py'];refs=s['pg1691_native_refs.py']
        for literal in ['LABEL="PG1544";Pg387TrustedDeployment.STEM="pg1544"','LABEL="PG1638";Pg387TrustedDeployment.STEM="pg1638"','4d6bcbddb417b76d27e52d5d9640752c300edccf','2741c4546afad6c1e8b6efbd53dfb58144edf7bb','2026-10-12T06:48:58.973359Z']:
            self.assertIn(literal,java)
        self.assertIn('phase="CANONICAL_INVALID"',java)
        self.assertIn('phase="ATOMIC_APPROVAL"',java)
        self.assertIn('transitionOriginal(epoch,done);',java)
        self.assertIn('/var/lib/pgpt-s1-preservation/pg1689-completed-candidate-host-ro-v1/after.private.json',refs)
        self.assertIn('pg1691_ordinary_publication_contract',refs)
        self.assertIn('pg1692_ordinary_exchange_io',refs)
        self.assertIn("OLD_LINK='/opt/schubert-nk/releases/0.1.0-PG1544'",oracle)
        self.assertIn("NEW_LINK='/opt/schubert-nk/releases/0.1.0-PG1638'",oracle)
        for old in ['PG1068','PG1292','cbca8738','9f651096','27accac0','2026-10-10T20:03']:
            self.assertNotIn(old,java+refs+oracle)
        for name,raw in s.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<ordinary fixed '+name+'>'))

    def test_exact_no_old_ro_dependency_and_new_import_closure(self):
        s=p.sources();pins=set(s)
        for name,raw in s.items():
            if name.endswith('.py'):
                for node in ast.walk(ast.parse(raw)):
                    modules=[a.name for a in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)else[]
                    for module in modules:
                        if module and module.startswith('pg'):self.assertIn(module.split('.')[0]+'.py',pins)
        self.assertIn('pg1691-completed-publication-tools-v1',s['pg1691_input_preflight.py'])
        self.assertIn('pg1694-completed-ordinary-publication-v1',s['Pg1691OrdinaryPublication.java'])
        self.assertNotIn('candidateReadOnly()',s['Pg1691OrdinaryPublication.java'])
        raw=compiler.compiler()
        self.assertIn("prior=json.loads((engine.W/'pg1687-frozen-v1.safe.json').read_bytes())",raw)
        self.assertIn("name.startswith(('Pg1686',))",raw)
        self.assertIn('pg1693-frozen-v1.safe.json',raw)
        self.assertIn('Pg1691TransitionTest',raw)


if __name__=='__main__':unittest.main()
