import inspect
import unittest
from pyflakes.api import checkPath
import pg6334_current4048_trace_test as previous
import pg6390_current4052_trace as subject


class Definition(unittest.TestCase):
    def test_exact4052_current_run_and_no_old_success_or_budget_import(self):
        scope = subject.definitions('a'*64, 'b'*64)
        values = scope['measurement'].__code__.co_consts
        for item in (4052, 608, 'PG6386-six-v1'):
            self.assertIn(item, values)
        for item in (4048, 4034, 607, 606, 'PG6330-six-v1', 'PG6244-six-v1'):
            self.assertNotIn(item, values)
        self.assertIn('PG6390-current943-trace-v1', scope['report'].__code__.co_consts)
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))


# Reuse the independent original candidate positive/mutated-byte, missing/duplicate,
# acceptance, measurement, cost and effort rejection vectors against current4052.
raw = inspect.getsource(previous.ActualOriginalCandidate)
for before, after in (
    ('5eb040421ae9ea06ecc70c6eb2e152871c2d0d42', 'aed19c6dca368e9717309d6f744d7917c6b7b32c'),
    ('(943,4048,607,0)', '(943,4052,608,0)'),
    ("'METHOD':687", "'METHOD':689"), ("'BRANCH':723", "'BRANCH':722")):
    if before not in raw:
        raise ValueError('explicit current4052 candidate fixture '+before)
    raw = raw.replace(before, after)
scope = {**vars(previous), '__name__': __name__, 'subject': subject}
exec(compile(raw, '<actual4052 current943 candidate>', 'exec'), scope)
ActualOriginalCandidate = scope['ActualOriginalCandidate']


if __name__ == '__main__':
    unittest.main()
