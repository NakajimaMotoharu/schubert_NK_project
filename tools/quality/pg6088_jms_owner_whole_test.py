import ast
import unittest
import pg6088_jms_owner_whole as p


class WholeDefinitionTest(unittest.TestCase):
    def test_all_named_declarations_including_unchanged_repeat10(self):
        self.assertEqual((3985, 595), p.declared_inventory())

    def test_full_counts_source_and_namespace_without_invocation(self):
        server = p.server_source(p.SOURCE, '0'*64)
        tree = ast.parse(server)
        for n, count in ((3985, 2), (595, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(tree)))
        self.assertIn('source-full-PG6088', server)
        self.assertNotIn('source-full-PG6060', server)
        driver = p.driver_source({})
        self.assertIn("'tests': 3985, 'suites': 595, 'mainClasses': 1667", driver)
        self.assertIn(p.SLOT, driver)


if __name__ == '__main__':
    unittest.main()
