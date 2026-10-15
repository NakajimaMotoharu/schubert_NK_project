import unittest
from pyflakes.api import check

from pg3340_concurrent_exec_oracle import ROOT, FILES, SERVER, mutate


class ConcurrentOracleTest(unittest.TestCase):
    def test_exact_actual_main_anchor_and_scoped_wrong_input(self):
        raw = (ROOT / FILES[1]).read_text(); wrong = mutate(raw)
        self.assertEqual(1, wrong.count('argv = List.of("PRIVATE_COMMON_WRONG")'))
        self.assertEqual(1, wrong.count('env.put("X", "PRIVATE_COMMON_WRONG")'))
        self.assertIn('argv.getFirst().startsWith("fixture")', wrong)
        for bad in ['', raw + raw, wrong]:
            with self.assertRaises(ValueError): mutate(bad)

    def test_complete_server_namespace_and_no_agent_or_vm_command(self):
        raw = 'INPUT={}\nfrom pg3340_concurrent_exec_oracle import require,mutate,fixed_jdk,launcher_path\n' + SERVER
        self.assertEqual(0, check(raw, '<exec oracle payload>'))
        self.assertNotIn('-javaagent:', SERVER)
        self.assertNotIn('systemctl', SERVER)
        self.assertIn('CANARY_ASSERTION_CAUSE=true', SERVER)


if __name__ == '__main__':
    unittest.main()
