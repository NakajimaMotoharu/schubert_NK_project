import inspect
import unittest
from pyflakes.api import checkPath
import pg6334_current4048_trace_test as previous
import pg6456_current4056_trace as subject


class Definition(unittest.TestCase):
    def test_exact4056_current_run_not_earlier_success(self):
        scope = subject.definitions('a'*64, 'b'*64)
        values = scope['measurement'].__code__.co_consts
        for item in (4056, 610, 'PG6452-six-v1'):
            self.assertIn(item, values)
        for item in (4054, 4052, 4048, 4034, 608, 607, 606, 'PG6408-six-v1'):
            self.assertNotIn(item, values)
        self.assertIn('PG6456-current943-trace-v1', scope['report'].__code__.co_consts)
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))


# Independent original XML comparison identifies two incidental concurrency-catch
# lines (BackupStartIntentFiles240/241) now missed. Do not import prior3554.
raw = inspect.getsource(previous.ActualOriginalCandidate)
for before, after in (
    ('5eb040421ae9ea06ecc70c6eb2e152871c2d0d42', '669ad5fd83f67ad031b2c1734d7fc5716599d35d'),
    ('(943,4048,607,0)', '(943,4056,610,0)'),
    ("'LINE':3554", "'LINE':3556"), ("'METHOD':687", "'METHOD':689"), ("'BRANCH':723", "'BRANCH':722")):
    if before not in raw:
        raise ValueError('explicit current4056 candidate fixture '+before)
    raw = raw.replace(before, after)
scope = {**vars(previous), '__name__': __name__, 'subject': subject}
exec(compile(raw, '<actual4056 current943 candidate>', 'exec'), scope)
ActualOriginalCandidate = scope['ActualOriginalCandidate']


if __name__ == '__main__':
    unittest.main()
