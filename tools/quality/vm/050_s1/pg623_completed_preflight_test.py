"""Only new proof slot/candidate fields differ; underlying genuine original checks remain exact."""
import ast
import unittest
import pg613_terminal_final
import pg623_completed_preflight


class CompletedPreflight(unittest.TestCase):
    def test_original_kernel_rows_and_owned_terminal_checks_retained_new_candidate_unused(self):
        actual=pg623_completed_preflight.payload()
        compile(actual,'<new unused cohort proof>','exec')
        receipt=(pg623_completed_preflight.R/'pg611_parent_receipt.py').read_text()
        self.assertIn('3a53b979-fa01-47dd-92a6-7b26affcfb5c',receipt)
        self.assertIn('970bbce1-6bba-4db0-ace1-680ee7dfde92',receipt)
        for literal in ('970bbce1-6bba-4db0-ace1-680ee7dfde92',
                        '87761979588','19b7e618ef04f79aff6cde2c2dbf45269c1f9651efaa44f04d81d84d02b85912',
                        'all24UnchangedTwice','allClientAdvisoryFlock0',
                        '0.1.0-PG600','0.1.0-PG621',
                        '4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e'):
            self.assertIn(literal,actual)
        old=ast.parse(pg613_terminal_final.PAYLOAD);new=ast.parse(actual)
        old_snapshot=next(n for n in ast.walk(old)if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
        new_snapshot=next(n for n in ast.walk(new)if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
        self.assertEqual(ast.dump(old_snapshot),ast.dump(new_snapshot))
        self.assertIn("save=base/'pg623-completed-preflight-v1'",actual)
        self.assertNotIn("save=base/'pg613-terminal-final-v1'",actual)
        self.assertIn("'activationNotRun':True",actual)
        self.assertNotIn('systemctl start',actual)
        self.assertNotIn('systemctl stop',actual)


if __name__=='__main__':unittest.main()
