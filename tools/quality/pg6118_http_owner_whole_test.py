import ast
import unittest
import pg6118_http_owner_whole as subject


class Definition(unittest.TestCase):
    def test_complete_current_declarations(self):
        self.assertEqual((3988, 595), subject.declared_inventory())

    def test_locked_dimensions_and_newonly_namespace(self):
        server = subject.server_source(subject.SOURCE, '0'*64)
        tree = ast.parse(server)
        for value, count in ((3988, 2), (595, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6118', server)
        self.assertNotIn('source-full-PG6088', server)
        driver = subject.driver_source({})
        self.assertIn("'tests': 3988, 'suites': 595, 'mainClasses': 1667", driver)
        self.assertIn(subject.SLOT, driver)


if __name__ == '__main__':
    unittest.main()
