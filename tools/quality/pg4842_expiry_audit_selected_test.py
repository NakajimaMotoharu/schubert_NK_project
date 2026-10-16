import ast
import unittest
import pg4842_expiry_audit_selected as role


class ExactHelpers(unittest.TestCase):
    def test_actual_scope_and_both_predicate_gates(self):
        role.validate_selection();raw=role.source();ast.parse(raw)
        self.assertIn(role.PROJECTS,raw)
        self.assertEqual(10,len(role.MODULES))
        self.assertEqual({'protocol','storage','bootstrap','api','web','batch'},set(role.MODULES.values()))
        self.assertIn("['verifyPriorAudit', 'verifyPriorExpiry']",raw)
        self.assertIn('conditions incomplete',raw)
        self.assertIn("'api.admittedConfiguration'",raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)
        self.assertIn('actual != expected',raw)
        self.assertIn("'actualMavenExit': code",raw)


if __name__=='__main__':unittest.main()
