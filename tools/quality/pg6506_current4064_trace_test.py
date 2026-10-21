import unittest
from unittest.mock import patch
from pathlib import Path
from pyflakes.api import checkPath
import pg6506_current4064_trace as subject
import pg6508_current4064_static_join as joined


class Definition(unittest.TestCase):
    def test_exact4064_run_dimensions_and_prior943_source(self):
        scope = subject.definitions('a'*64, 'b'*64)
        constants = scope['measurement'].__code__.co_consts
        for value in (4064, 612, 'PG6490-six-v1'): self.assertIn(value, constants)
        for value in (4056, 610, 'PG6452-six-v1', 4034, 606): self.assertNotIn(value, constants)
        self.assertIn('PG6506-current943-trace-v1', scope['report'].__code__.co_consts)

    def test_failed_original_is_not_a_missing_result_replay(self):
        with patch.object(Path,'read_bytes',return_value=b'{}'), patch.object(subject.json,'loads',side_effect=[{'actualExit':1},{'actualExit':0}]):
            with self.assertRaisesRegex(ValueError,'genuine original4064'):
                subject.read_qualified()

    def test_static_join_requires_actual4064_and_original27(self):
        constants = joined.definitions()['main'].__code__.co_consts
        self.assertIn(4064,constants)
        self.assertIn('PG6500-web-owned-component-qualification-v5/manifest.json',constants)
        self.assertIn('PG6508-current4064-static-join-v1',constants)
        for path in (subject.__file__,joined.__file__,__file__): self.assertEqual(0,checkPath(path))


if __name__ == '__main__': unittest.main()
