import unittest
from pyflakes.api import check
import pg6032_error_boundary_corrected as t


class Corrective965RunnerTest(unittest.TestCase):
    def test_separate_namespace_and_complete_driver(self):
        names = sorted(k for k in vars(t.previous) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\n'+t.driver_source(), '<corrective965 complete namespace>'))
        self.assertNotIn("'pg6026-error-boundary-selected965-v1'", t.driver_source())
        self.assertIn("'pg6032-error-boundary-selected965-v1'", t.driver_source())
        self.assertEqual((162, 965), tuple(map(lambda f: f(t.previous.inventory()[1]), (len, lambda c: sum(c.values())))))


if __name__ == '__main__':
    unittest.main()
