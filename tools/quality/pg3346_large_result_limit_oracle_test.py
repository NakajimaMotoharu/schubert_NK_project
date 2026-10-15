import inspect
import unittest
from pyflakes.api import check

import pg3346_large_result_limit_oracle as target


class MaximumOracleTest(unittest.TestCase):
    def test_actual_main_two_consistent_lowered_bounds_only(self):
        raw = (target.engine.ROOT / target.FILES[1]).read_text()
        mutated = target.mutate(raw)
        self.assertIn('MAXIMUM_RECORD_COUNT = 9_999;', mutated)
        self.assertIn('MAXIMUM_BYTE_LENGTH = 47_995_200L;', mutated)
        self.assertEqual(raw.replace('10_000;', '9_999;').replace('48_000_000L;', '47_995_200L;'), mutated)
        for invalid in ['', raw + raw, mutated]:
            with self.assertRaises(ValueError): target.mutate(invalid)

    def test_two_actual_vectors_and_standalone_transmitted_mutator(self):
        mutation = inspect.getsource(target.mutate).replace('engine.require(', 'require(')
        raw = 'INPUT={}\nfrom pg3340_concurrent_exec_oracle import require,fixed_jdk,launcher_path\n' + mutation + '\n' + target.server()
        self.assertEqual(0, check(raw, '<fixed maximum complete namespace>'))
        self.assertIn('source-full-PG3302/src/schubert-nk-protocol/target', raw)
        self.assertIn("('LOWERED_MAXIMUM','largeResultMaximum',True)", raw)
        self.assertNotIn('LinuxProcessExec', raw)
        self.assertIn('CANARY_ASSERTION_CAUSE=true', raw)


if __name__ == '__main__':
    unittest.main()
