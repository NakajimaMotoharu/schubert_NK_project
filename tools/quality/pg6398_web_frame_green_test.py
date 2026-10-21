import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6398_web_frame_green as subject
import pg6400_web_frame_qualification as qualification


class Definition(unittest.TestCase):
    def test_actual25_related_declarations_and_unbound_red_fail_closed(self):
        _, counts = subject.inventory(draft=True)
        self.assertEqual((25, 11), (sum(counts.values()), len(counts)))
        self.assertEqual(1, counts['dev.codex.schubert.nk.web.bootstrap.WebRuntimeExecutionRetentionTest'])
        with patch.object(subject, 'RED_SOURCE', None), self.assertRaisesRegex(ValueError, 'bind genuine red'):
            subject.guard_source('HEAD')
        for path in (subject.__file__, qualification.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
