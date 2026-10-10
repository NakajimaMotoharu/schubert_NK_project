import ast
import unittest
from pg1293_completed_unused_stage_sources import sources,BASELINE_SHA


class CompletedPlacementContractTest(unittest.TestCase):
    def test_same_genuine_done_and_one_closed_placement_not_stop_or_cold(self):
        files=sources();java=files['Pg1293UnusedStage.java'];refs=files['pg1293_native_refs.py'];helper=files['pg1293_native_owned_stop.py']
        for n,s in files.items():
            if n.endswith('.py'):ast.parse(s)
        self.assertIn('"place".equals(args[0])',java)
        self.assertIn('refs.check("place")',java)
        self.assertNotIn('refs.check("stop:',java)
        self.assertIn('State.ISSUED',java)
        self.assertIn('2026-10-10T20:22:34.439375Z',java)
        self.assertIn(BASELINE_SHA,refs)
        self.assertIn('same_value(first,prior)',refs)
        self.assertIn('require(not placed);place_candidate();placed=True',refs)
        self.assertNotIn('systemctl\', \'stop',helper)
        self.assertNotIn('def stop_one',helper)
        self.assertIn("b'Pg1293UnusedStage', b'place'",ast.unparse(ast.parse(helper)))
        self.assertIn('PG998-native-stage',refs)
        self.assertIn('SOURCE=\'769ddb15',refs)

    def test_actual_generated_family_and_finite_action_negative_vectors(self):
        helper=sources()['pg1293_native_owned_stop.py'];tree=ast.parse(helper)
        names={'require','placement_family','placement_action'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
        self.assertEqual(len(nodes),3);env={}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual stage pure boundary>', 'exec'),env)
        family=env['placement_family'];action=env['placement_action']
        good=[b'/opt/jdk-25.0.4/bin/java',b'-cp',b'fixed',b'Pg1293UnusedStage',b'place',b'']
        self.assertTrue(family(good))
        for bad in [None,[],good[:-1],good[:-2]+[b'stop',b''],[b'/other/java']+good[1:],good[:-3]+[b'Pg1253NativeStop',b'place',b''],good[:-1]+[None]]:
            self.assertFalse(family(bad))
        for value in [('before',False),('before',True),('place',False),('terminal',True),('release',True)]:
            self.assertTrue(action(*value))
        for value in [(None,False),('stop',False),('place',True),('terminal',False),('release',False),('before',None),('before',0)]:
            with self.assertRaises(ValueError):action(*value)


if __name__=='__main__':unittest.main()
