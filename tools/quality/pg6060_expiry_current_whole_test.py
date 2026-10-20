import ast
import unittest
import pg6060_expiry_current_whole as t


class WholeDefinitionNoInvocationTest(unittest.TestCase):
    def test_declared_inventory_expands_only_the_unchanged_existing_repeat10(self):
        self.assertEqual((3979, 594), t.declared_inventory())

    def test_complete_fixed_source_namespaces_and_explicit_current_counts(self):
        server = t.server_source('a'*40, '0'*64)
        tree = ast.parse(server)
        for n, count in ((3979, 2), (594, 1), (1667, 1)):
            self.assertEqual(count, sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(tree)))
        self.assertIn('source-full-PG6060', server)
        self.assertNotIn('source-full-PG6040', server)
        driver = t.driver_source({})
        self.assertIn("'tests': 3979, 'suites': 594, 'mainClasses': 1667", driver)
        self.assertIn(t.SLOT, driver)
        for forbidden in ('systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(forbidden, server)


if __name__ == '__main__':
    unittest.main()
