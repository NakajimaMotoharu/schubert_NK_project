import hashlib
import subprocess
import unittest
import pg5248_startup_view_selected as role


class TypedCatchViewScope(unittest.TestCase):
    def test_fixed_golden_and_all8_java_tests_are_byte_identical_to_failed673(self):
        path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupAdmissionViewOwnerTest.java'
        old=subprocess.check_output(['git','show','673888c95a6a3de6b0c7884e9a80e25242f131bf:'+path],cwd=role.selected.ROOT)
        self.assertEqual(hashlib.sha256(old).hexdigest(),role.selected.sha(role.selected.ROOT/path))
        self.assertEqual(old.count(b'@Test'),8)
        self.assertEqual(len(role.extra_suites()),67)

    def test_only_predeclared_owner_and_outer_semantics_plus_bounded_dependencies(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),25)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),55)


if __name__=='__main__':unittest.main()
