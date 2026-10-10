"""Independent v3 family literal contract and dispatch/compiler slot invariants."""
import ast
import unittest
from pg1079_cold_candidate_sources_v3 import files
from pg1080_cold_candidate_compile_v3 import source as compiler
from pg1081_cold_candidate_native_v3 import source as transport


class Family(unittest.TestCase):
    def test_current_and_candidate_scopes_and_fixed_operation(self):
        values=files()
        self.assertEqual({'Pg1079ColdCandidateStage.java','Pg1079ColdCandidateStageTest.java','pg1079_cold_refs.py'},set(values))
        java=values['Pg1079ColdCandidateStage.java'];py=values['pg1079_cold_refs.py']
        self.assertIn('"place".equals(args[0])',java)
        self.assertIn("[b'Pg1079ColdCandidateStage',b'place',b'']",py)
        self.assertIn('def place_candidate():',py)
        self.assertIn('/home/ubuntu/pg1081-candidate-input-v1',py)
        self.assertIn('/var/lib/pgpt-s1-preservation/pg1079-cold-candidate-v1',py)
        ast.parse(py)
        for source in values.values():
            self.assertNotIn('pg1074-cold-candidate-v1',source)
            self.assertNotIn('Pg1074ColdCandidateStage',source)

    def test_compiler_transport_source_and_actions_are_same_new_family(self):
        compile_source=compiler();native_source=transport()
        ast.parse(compile_source);ast.parse(native_source)
        self.assertIn('pg1080-cold-candidate-frozen-v3.safe.json',compile_source)
        self.assertIn('pg1080-cold-candidate-frozen-v3.safe.json',native_source)
        self.assertIn('Pg1079ColdCandidateStage',native_source)
        self.assertIn("('stage','place')",native_source)
        self.assertIn('pg1081-release-v1.tar',compile_source)
        self.assertIn('pg1081-release-v1.tar',native_source)
        self.assertNotIn('pg1076-place-v1',native_source)


if __name__=='__main__':unittest.main()
