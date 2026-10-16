"""Whole independent oracle and current immutable bindings, no guest actions."""
import ast
import unittest
import pg3858_current_resume_acceptance as actual
import pg3582_current_browser_acceptance as previous


class OracleTest(unittest.TestCase):
    def test_terminal(self):
        raw=actual.terminal_payload(actual.live()['binding']);ast.parse(raw)
        self.assertIn(actual.TERM,raw);self.assertIn('PG3748',raw)
        self.assertNotIn('PG3420',raw)

    def test_independent_rows(self):
        raw=actual.rows_payload();ast.parse(raw)
        self.assertIn(actual.oracle_source(),raw)
        for text in [actual.ONCE,actual.ROWS,actual.RUN,actual.before(),"protected_count']==10",'newSkippedSteps',actual.SOURCE,actual.BOM]:self.assertIn(text,raw)
        self.assertEqual(previous.oracle_source(),actual.oracle_source())

    def test_full_seal_nested_oracles(self):
        raw=actual.seal_payload(actual.live()['binding']);ast.parse(raw)
        self.assertIn(actual.SEAL,raw);self.assertIn(actual.before(),raw)
        values={node.targets[0].id:ast.literal_eval(node.value)for node in ast.parse(raw).body if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in {'ORACLE','GUARD'}}
        self.assertIn(actual.oracle_source().split('def qualify(')[0],values['ORACLE'])
        self.assertIn('qualify_resume',values['ORACLE'])
        self.assertIn(actual.live()['binding']['activation'],values['GUARD'])
        self.assertIn(actual.SOURCE,values['GUARD'])
        self.assertIn('PG3748',values['GUARD'])
        self.assertNotIn('PG3420',raw)


if __name__=='__main__':unittest.main()
