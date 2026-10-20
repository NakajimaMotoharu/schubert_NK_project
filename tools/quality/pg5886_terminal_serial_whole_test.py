import ast
import subprocess
import unittest
import pg5886_terminal_serial_whole as target


class Coherent3973Test(unittest.TestCase):
    def test_exact_inventory_source_and_unmodified_gate_profile(self):
        self.assertEqual(subprocess.check_output(['git','rev-parse','79098cfa5'],cwd=target.ROOT,text=True).strip(),target.SOURCE)
        raw=target.server_source(target.SOURCE,'a'*64);values=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        for n in(3973,592,1666):self.assertIn(n,values)
        self.assertNotIn(3971,values);self.assertIn('source-full-PG5886',raw);self.assertNotIn('PG5860',raw)
        self.assertNotIn('failIfNoTests=false',raw)
        driver=target.driver_source({});self.assertIn('pg5886-terminal-serial-six-v1',driver)
        self.assertIn("'tests': 3973, 'suites': 592, 'mainClasses': 1666",driver)


if __name__=='__main__':unittest.main()
