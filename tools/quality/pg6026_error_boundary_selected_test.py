import unittest
from pyflakes.api import check
import pg6026_error_boundary_selected as t


class AffectedBoundaryRunnerTest(unittest.TestCase):
    def test_complete_namespace_and_explicit_inventory(self):
        names = sorted(k for k in vars(t.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        raw = t.runner_source()
        self.assertEqual(0, check('='.join(names)+'=None\nCOUNTS=NODE_PATH=None\n'+raw, '<boundary965 complete namespace>'))
        self.assertIn('len(physical)==1667', raw)
        self.assertIn('len(target_counters)==2', raw)
        cases, counts, targets = t.inventory()
        self.assertEqual((162, 965), (len(counts), sum(counts.values())))
        self.assertEqual(143, len(cases['web']))
        self.assertEqual(2, sum(map(len, targets.values())))
        for forbidden in ('systemctl', 'qemu-system', 'sudo ', '--recover', '--resume', '/opt/schubert-nk/current'):
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
