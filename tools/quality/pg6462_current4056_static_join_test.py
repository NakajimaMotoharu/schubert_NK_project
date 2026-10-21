import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6462_current4056_static_join as subject
import pg6456_current4056_trace as trace


class Definition(unittest.TestCase):
    def test_exact4056_source_23_static_and_no_older_measurement(self):
        values = subject.definitions()['main'].__code__.co_consts
        for value in (4056, 1361, 'PG6450-morning-sequence-qualification-v1/manifest.json',
                      'PG6452-six-v1', 'PG6462-current4056-static-join-v1'):
            self.assertIn(value, values)
        values = trace.definitions('a'*64, 'b'*64)['measurement'].__code__.co_consts
        for value in (4056, 610, 'PG6452-six-v1'):
            self.assertIn(value, values)
        for value in (4054, 4052, 4034, 608, 606, 'PG6408-six-v1'):
            self.assertNotIn(value, values)
        for path in (subject.__file__, trace.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_begin_or_missing_original_cannot_become_semantic_success(self):
        with patch.object(subject, 'read_qualified', side_effect=ValueError('unreturned original4056')):
            with self.assertRaisesRegex(ValueError, 'unreturned original4056'):
                subject.main()


if __name__ == '__main__':
    unittest.main()
