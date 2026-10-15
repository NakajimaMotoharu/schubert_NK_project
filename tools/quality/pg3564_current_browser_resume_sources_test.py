"""Independent final role/authority boundaries; no guest write or Source PT credit."""
import ast
import unittest
import pg3564_current_browser_resume_sources as p


class FinalRoles(unittest.TestCase):
    def test_all_twenty_current_emissions(self):
        values=p.sources()
        self.assertEqual(20,len(values))
        java=values[p.CLASS+'.java']
        self.assertIn('LABEL="PG3420";Pg387TrustedDeployment.STEM="pg3420"',java)
        self.assertIn('endedAt().equals(java.time.Instant.parse("2026-10-15T17:16:54.836275Z"))',java)
        self.assertIn('independentChecks=',values['Pg3564OriginalTupleTest.java'])
        refs=values['pg3564_native_refs.py']
        self.assertIn(p.BASELINE,refs)
        self.assertIn('admit_existing_runtime(runtime_before',refs)
        self.assertIn("'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))",refs)
        self.assertIn('zz-pg3564-once-resume.conf',values['pg3564_runtime_writer.py'])

    def test_numeric_binding_does_not_damage_hashes(self):
        digest='a18100986959b122976c19749542200d'
        self.assertEqual(digest,p.bind(digest))
        self.assertEqual('START = 82190409233\n/proc/321930',p.bind('START = 18100986959\n/proc/122976'))

    def test_full_snapshot_direct_actual_native(self):
        tree=ast.parse(p.sources()['pg3564_native_refs.py'])
        fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='capture_data')
        ret=next(n.value for n in ast.walk(fn) if isinstance(n,ast.Return) and isinstance(n.value,ast.Dict))
        self.assertEqual(11,len(ret.keys))
        native=ret.values[[k.value for k in ret.keys].index('native')]
        self.assertIsInstance(native,ast.Call)
        self.assertEqual('tree',native.func.id)


if __name__=='__main__': unittest.main()
