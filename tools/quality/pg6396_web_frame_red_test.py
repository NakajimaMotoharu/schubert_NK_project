import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6396_web_frame_red as subject


class Definition(unittest.TestCase):
    def test_draft_single_method_nine_modes_not_nine_production_tests(self):
        _, counts = subject.inventory(draft=True)
        self.assertEqual((15, 9), (sum(counts.values()), len(counts)))
        self.assertEqual(1, counts['dev.codex.schubert.nk.web.bootstrap.WebRuntimeExecutionRetentionTest'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_unreturned_original_whole_cannot_be_replaced_by_a_begin(self):
        with patch.object(subject, 'WHOLE_QUALIFICATION_SHA', None), self.assertRaisesRegex(ValueError, 'bind actual original4052'):
            subject.original4052()
        raw = subject.runner_source(15, 9)
        compile(raw, '<unchanged normal selected runner>', 'exec')
        for token in ('qemu-system', 'systemctl', '--recover', '--resume', '/opt/schubert-nk/current'):
            self.assertNotIn(token, raw)


if __name__ == '__main__':
    unittest.main()
