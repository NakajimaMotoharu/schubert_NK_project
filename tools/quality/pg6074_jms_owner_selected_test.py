import unittest
import pg6074_jms_owner_selected as t


class OwnershipProfileDefinitionTest(unittest.TestCase):
    def test_all_api_web_and_six_guards_explicit_four_target_gate_node_and_no_operations(self):
        cases, counts = t.inventory()
        self.assertEqual(set(t.engine.MODULES), set(cases))
        self.assertEqual((1933, 317), (sum(counts.values()), len(counts)))
        raw = t.runner_source(sum(counts.values()), len(counts))
        self.assertIn('target100=len(target_counters)==4', raw)
        self.assertIn('done=done and target100', raw)
        self.assertIn('NODE_PATH', raw)
        for operation in ('systemctl', 'qemu-system', 'sudo ', '--resume', '--recover', '/opt/schubert-nk/current'):
            self.assertNotIn(operation, raw)


if __name__ == '__main__':
    unittest.main()
