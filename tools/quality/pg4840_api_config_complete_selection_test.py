import ast
import unittest
import pg4840_api_config_complete_selection as role


class AllRequiredModules(unittest.TestCase):
    def test_physical_suites_and_strict_actual_command(self):
        role.validate_selection()
        self.assertEqual({'protocol','storage','bootstrap','api'},set(role.MODULES.values()))
        self.assertEqual(7,len(role.MODULES))
        raw=role.source();ast.parse(raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)
        self.assertIn('target coverage absent; not executed or failed, never accepted',raw)
        self.assertIn('selected identity inventory differs',raw)
        self.assertIn("module = MODULES[name]",raw)
        self.assertIn("'actualMavenExit': code",raw)


if __name__=='__main__':unittest.main()
