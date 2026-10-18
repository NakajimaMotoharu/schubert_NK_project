import re
import unittest
import pg5232_caddy_child_selected as role


class CaddyChildScope(unittest.TestCase):
    def test_existing_three_caddy_cases_and_native_child_already_in_allbootstrap(self):
        source=role.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CaddyPublicConfigurationTest.java'
        self.assertEqual(len(re.findall(r'@Test\s+void\s+\w+\(',source.read_text())),3)
        self.assertEqual(len(role.extra_suites()),65)
        self.assertIn('dev.codex.schubert.nk.bootstrap.ChildStartupContextTest',role.extra_suites())

    def test_two_exact_main_changes_no_debug_or_new_class_permission_added(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),23)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),48)
        self.assertEqual(len(role.KEYS),2)


if __name__=='__main__':unittest.main()
