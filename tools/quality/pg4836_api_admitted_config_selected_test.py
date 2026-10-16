import ast
import unittest
import pg4836_api_admitted_config_selected as role


class ExactApiSnapshot(unittest.TestCase):
    def test_module_and_actual_helper_counter_gate(self):
        raw=role.source();ast.parse(raw)
        self.assertIn("module = MODULES[name]",raw)
        self.assertIn("'-pl', 'src/schubert-nk-api'",raw)
        self.assertIn("m.get('name')=='admittedConfiguration'",raw)
        self.assertIn("all actual helper lines/method/conditions must be covered",raw)
        self.assertIn("if actual != expected",raw)
        self.assertIn("fixed input changed",raw)
        self.assertIn("deployed825e remains unchanged",raw)
        self.assertEqual(set(role.MODULES.values()),{'api'})
        self.assertEqual(4,len(role.TESTS))


if __name__=='__main__':unittest.main()
