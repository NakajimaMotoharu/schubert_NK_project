import ast
import unittest
import pg5888_terminal_serial_qualification as target


class Independent3973ReaderTest(unittest.TestCase):
    def test_exact_current_and_prior_inventory_complete_namespaces(self):
        self.assertEqual(2,len(target.added_cases()));self.assertEqual(3,len(target.PHYSICAL_KINDS))
        raw=target.emitted({});values=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        for n in(3973,3971,592,1666,1663):self.assertIn(n,values)
        self.assertIn('source-full-PG5886',raw);self.assertNotIn('source-full-PG5860',raw)
        self.assertNotIn('Popen',raw);self.assertNotIn('subprocess.run',raw)
        self.assertIn('PG5888-qualified-v1',target.operator_source())


if __name__=='__main__':unittest.main()
