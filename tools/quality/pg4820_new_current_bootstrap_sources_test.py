"""Independent bindings and no stale operation eligibility; no VM actions."""
import ast
import unittest
from unittest.mock import patch
import pg4820_new_current_bootstrap_sources as role


class CurrentBootstrap(unittest.TestCase):
    def test_current_closure(self):
        values=role.files(role.BASELINE)
        java=values['Pg4820BootstrapExisting.java'];helper=values['pg4820_bootstrap_existing.py']
        self.assertIn('expectedBeforeOwnership(2,"schubert_batch","PG4820-bootstrap-guard"',java)
        self.assertEqual(java.count('static Pg4820OwnedDatabase.Expected expectedBeforeOwnership('),1)
        self.assertIn('==874',helper);self.assertIn(role.BASELINE,helper)
        self.assertIn(role.before.SLOT,helper);self.assertIn('189659374308',helper)
        self.assertIn('b414b0e1e5ac47e8b5fb8c5ae3d94348',helper)
        self.assertIn(role.SOURCE,java);self.assertIn(role.BOM,values['pg4820_input_preflight.py'])
        self.assertEqual(values['pg4772_parent_receipt.py'],(role.W/'pg4772-new-current-owned-tools-v1/pg4772_parent_receipt.py').read_text())
        self.assertIn('path,closing',values['pg4820_bootstrap_contract.py'])
        self.assertIn('PG[0-9]{3,4}-',values['Pg4820OwnedDatabase.java'])
        for name,text in values.items():
            if name.endswith('.py'):ast.parse(text)
            for stale in ('2741c454','PG1638','pg1718-current','Pg1719','Pg1728','pg1703_parent_receipt'):
                self.assertNotIn(stale,text,name)

    def test_no_old_success_can_authorize(self):
        with self.assertRaisesRegex(ValueError,'actual4818'):role.files('0'*64)
        with patch.object(role,'eligibility',side_effect=ValueError('not qualified')):
            with self.assertRaisesRegex(ValueError,'not qualified'):role.files(role.BASELINE)


if __name__=='__main__':unittest.main()
