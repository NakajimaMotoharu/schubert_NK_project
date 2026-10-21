import unittest
from pyflakes.api import checkPath
import pg6402_web_frame_order as subject


class Definition(unittest.TestCase):
    def test_actual_sealed25_main_has_two_exact_holding_frames(self):
        _, raw = subject.read(subject.W/'pg6398-web-frame-green-v1/source')
        rows = subject.analyze(subject.methods(raw))
        self.assertEqual(2, len(rows)); self.assertTrue(all(len(r['fenceOffsets']) == 5 for r in rows))
        self.assertEqual(4, subject.no_branches(subject.methods(raw))['methodCount'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_fence_or_error_handler_cannot_prove_holding(self):
        _, raw = subject.read(subject.W/'pg6398-web-frame-green-v1/source')
        for bad in (raw.replace('Reference.reachabilityFence:', 'Reference.notAFence:', 1),
                    raw.replace('Class java/lang/Error', 'Class java/lang/RuntimeException', 1)):
            with self.assertRaises(ValueError):
                subject.analyze(subject.methods(bad))


if __name__ == '__main__':
    unittest.main()
