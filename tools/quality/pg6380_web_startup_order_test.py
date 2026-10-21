import unittest
from pyflakes.api import checkPath
import pg6380_web_startup_order as subject


class Definition(unittest.TestCase):
    def test_actual_qualified_two_main_loop_and_four_fences(self):
        root = subject.W/'pg6370-web-startup-retry-v1/source'
        _, text = subject.read_jar(root, 'web', subject.WEB)
        blocks = subject.methods(text)
        code = next(v for k, v in blocks.items() if ' closeStartupResource(' in k)
        value = subject.retention(code)
        self.assertEqual(4, len(value['fenceOffsets'])); self.assertEqual(0, value['newRetentionAllocations'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_fence_backedge_or_close_handler_fails(self):
        _, text = subject.read_jar(subject.W/'pg6370-web-startup-retry-v1/source', 'web', subject.WEB)
        code = next(v for k, v in subject.methods(text).items() if ' closeStartupResource(' in k)
        bad = code.replace('Reference.reachabilityFence:', 'Reference.notAFence:', 1)
        with self.assertRaises(ValueError):
            subject.retention(bad)
        bad = code.replace('Class java/lang/Error', 'Class java/lang/RuntimeException')
        with self.assertRaises(ValueError):
            subject.retention(bad)


if __name__ == '__main__':
    unittest.main()
