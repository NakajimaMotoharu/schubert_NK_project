"""Explicit finite two modes and private-only inspect return before any placement."""
import ast
import unittest
import pg4454_inspectable_failed_unused_sources as tool


class InspectThenPlace(unittest.TestCase):
    def test_actual_inspect_branch_returns_before_release_or_signature_writes(self):
        values = tool.sources(); self.assertEqual(18, len(values))
        self.assertTrue(tool.inspection_has_no_release_writes(values['pg4444_native_refs.py']))
        raw = values['pg4444_native_refs.py']
        self.assertIn('place_candidate(INSPECT_ONLY)', raw)
        self.assertIn('candidate-manifest-inspect.private.json', raw)
        self.assertIn('check_data(capture_data(True))', raw)
        java = values['Pg4444UnusedStage.java']
        self.assertIn('inspectOnly=inspection(args)', java)
        self.assertIn('inspectOnly?"inspect":"place"', java)
        self.assertIn(tool.PROOF_SAVE, java)
        self.assertIn('"+(!inspectOnly)+"', java)

    def test_actual_owner_family_allows_only_same_java_and_two_literal_modes(self):
        values = tool.sources(); tree = ast.parse(values['pg4444_native_owned_stop.py'])
        nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','placement_family','placement_action']]
        self.assertEqual(3, len(nodes)); namespace = {}
        exec(compile(ast.Module(body=nodes,type_ignores=[]), '<actual finite owner family>', 'exec'), namespace)
        fixed = [b'/opt/jdk-25.0.4/bin/java',b'Pg4444UnusedStage',b'place',b'']
        self.assertTrue(namespace['placement_family'](fixed))
        inspect = list(fixed); inspect[-2] = b'inspect'; self.assertTrue(namespace['placement_family'](inspect))
        for index, value in [(0,b'/foreign/java'),(-3,b'Pg3982UnusedStage'),(-2,b'other'),(-1,b'foreign')]:
            changed = list(fixed); changed[index] = value
            self.assertFalse(namespace['placement_family'](changed))
        for action, placed in [('place',True),('terminal',False),('release',False),('unknown',False)]:
            with self.assertRaises(ValueError): namespace['placement_action'](action,placed)


if __name__ == '__main__':
    unittest.main()
