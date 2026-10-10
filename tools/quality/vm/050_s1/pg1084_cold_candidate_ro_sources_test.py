"""Independent read-only preparation, same family argv, RO ordering and no placement."""
import ast
import unittest
from pg1084_cold_candidate_ro_sources import files


class Ro(unittest.TestCase):
    def test_new_family_and_exact_mode(self):
        value=files()
        self.assertEqual({'Pg1084ColdCandidateRo.java','Pg1084ColdCandidateRoTest.java','pg1084_cold_refs.py'},set(value))
        java=value['Pg1084ColdCandidateRo.java'];py=value['pg1084_cold_refs.py']
        ast.parse(py)
        self.assertIn('"prepare-ro".equals(args[0])',java)
        self.assertIn("[b'Pg1084ColdCandidateRo',b'prepare-ro',b'']",py)
        self.assertNotIn('place_candidate()',py)
        self.assertNotIn('tar.extractall',py)
        self.assertNotIn('pg1081-candidate-input-v1',py)
        self.assertNotIn('environment()',java)
        self.assertNotIn('invalidate(',java)
        self.assertNotIn('Files.move(',java)

    def test_old_full_then_known_ro_new_full_then_old_restore_then_post(self):
        java=files()['Pg1084ColdCandidateRo.java']
        names=['IMMUTABLE_FULL_VERIFIER','CANDIDATE_HOST_NAMESPACE','NECESSARY_CANDIDATE_HOST_RO','FULL_IMMUTABLE_CANDIDATE']
        points=[java.index('phase="'+name+'"')for name in names]
        self.assertEqual(sorted(points),points)
        self.assertIn('!fields[4].equals(target)&&!fields[4].startsWith(target+"/")',java)
        self.assertIn('readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),target)',java)
        self.assertIn('new String[]{"prepare-ro"}',files()['Pg1084ColdCandidateRoTest.java'])
        self.assertIn('PG835_FIXED_MOUNT_ORACLE',files()['Pg1084ColdCandidateRoTest.java'])
        self.assertIn("candidateImmutableVerified=true",java)
        self.assertIn("contract.HeldInventory(str(candidate_root)",files()['pg1084_cold_refs.py'])
        py=files()['pg1084_cold_refs.py']
        self.assertLess(py.index('contract.HeldInventory(str(candidate_root)'),py.index("print('REF_READY'"))
        self.assertLess(py.index("phase='CANDIDATE_RO_POST'"),py.index('candidate_options='))


if __name__=='__main__':unittest.main()
