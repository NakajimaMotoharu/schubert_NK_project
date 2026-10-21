import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6406_current4052_static_join as subject


class Definition(unittest.TestCase):
    def test_actual_source_and_whole_bindings_not_old_pass(self):
        values = subject.definitions()['main'].__code__.co_consts
        for value in (4052, 1355, 'PG6384-web-fatal-callback-retry-qualification-v1/manifest.json',
                      'PG6386-six-v1', 'PG6406-current4052-static-join-v1'):
            self.assertIn(value, values)
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_whole_prevents_any_current_join_output(self):
        with patch.object(subject, 'read_qualified', side_effect=ValueError('unreturned original whole')):
            with self.assertRaisesRegex(ValueError, 'unreturned original whole'):
                subject.main()


if __name__ == '__main__':
    unittest.main()
