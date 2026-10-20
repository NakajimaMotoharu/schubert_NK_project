"""Operator-only inventory and generated command guards; Production PT credit zero."""
import unittest
import pg6080_web_factory_selected as p


class SelectionTest(unittest.TestCase):
    def test_explicit_source_inventory_and_target(self):
        cases, counts = p.inventory()
        self.assertEqual((925, 150), (sum(counts.values()), len(counts)))
        self.assertEqual(917, sum(n for c, n in counts.items() if c.removeprefix(p.engine.PACKAGE) in cases['web']))
        self.assertEqual(3, counts[p.engine.PACKAGE+'web.messaging.WebBrokerFactoryOwnershipTest'])
        self.assertEqual(6, len(cases))

    def test_real_runner_keeps_normal_command_and_gate(self):
        raw = p.runner_source()
        self.assertIn('done=done and target100', raw)
        self.assertIn('len(physical)==1667', raw)
        self.assertIn('target100=len(target_counters)==1', raw)
        self.assertIn('os.pathsep+NODE_PATH,MAVEN_OPTS', raw)
        self.assertIn("'expectedTests':925", raw)
        self.assertIn("'spotless:check'", raw)
        self.assertNotIn('sudo', raw)


if __name__ == '__main__':
    unittest.main()
