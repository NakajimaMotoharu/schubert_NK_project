"""Independent literal counts/negative outcomes and original quality order; no host invocation."""
import inspect
import unittest
from pyflakes.api import check, checkPath
import pg5128_root_full as role


class RootWhole(unittest.TestCase):
    def test_strict_literal_whole_counts_and_negative_results(self):
        raw = role.server_source(role.SOURCE, 'b' * 64)
        self.assertEqual(0, check(raw, '<complete new Root full>'))
        ns = {'__name__': 'pure_inspection_no_io'}
        exec(compile(raw, '<definitions only>', 'exec'), ns)
        good = [0, True, [], 3814, 556, 1654]
        self.assertTrue(ns['complete_result'](*good))
        for index, values in {0: [1, 143, True, None], 1: [False, None], 2: [['error'], None],
                              3: [3791, 3813, 3815], 4: [553, 555, 557], 5: [1650, 1653, 1655]}.items():
            for value in values:
                args = good.copy(); args[index] = value
                self.assertFalse(ns['complete_result'](*args))
        self.assertIn(role.SOURCE, raw)
        self.assertNotIn(role.previous.SOURCE, raw)
        self.assertLess(raw.index('    format_preflight(args,'), raw.index("with (OUT / 'maven.private.log')"))
        self.assertIn('format-before-pt.safe.json', raw)
        self.assertIn('PG5128', raw)
        self.assertNotIn('PG4968', raw)

    def test_clean_source_gate_selection_and_complete_namespace(self):
        raw = inspect.getsource(role.main)
        for literal in ("selected['tests'] == 50", "selected['suites'] == 8", "selected['phaseExits'] == [0, 0]",
                        "selected_role.main_delta(path / 'source', 'pending')", "'tests': 3814, 'suites': 556, 'mainClasses': 1654"):
            self.assertIn(literal, raw)
        for path in (role.__file__, __file__): self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
