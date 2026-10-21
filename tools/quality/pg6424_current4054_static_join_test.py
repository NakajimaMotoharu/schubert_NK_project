import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6424_current4054_static_join as subject
import pg6420_current4054_trace as trace


class Definition(unittest.TestCase):
    def test_exact4054_source_and_original26_bindings(self):
        values = subject.definitions()['main'].__code__.co_consts
        for value in (4054, 1358, 'PG6414-web-frame-pending-qualification-v1/manifest.json',
                      'PG6408-six-v1', 'PG6424-current4054-static-join-v1'):
            self.assertIn(value, values)
        values = trace.definitions('a'*64, 'b'*64)['measurement'].__code__.co_consts
        for value in (4054, 610, 'PG6408-six-v1'):
            self.assertIn(value, values)
        for path in (subject.__file__, trace.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_original_whole_cannot_become_source_join(self):
        with patch.object(subject, 'read_qualified', side_effect=ValueError('unreturned original4054')):
            with self.assertRaisesRegex(ValueError, 'unreturned original4054'):
                subject.main()


if __name__ == '__main__':
    unittest.main()
