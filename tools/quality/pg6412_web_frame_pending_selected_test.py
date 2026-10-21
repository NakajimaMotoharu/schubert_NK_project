import unittest
from pyflakes.api import checkPath
import pg6412_web_frame_pending_selected as subject
import pg6414_web_frame_pending_qualification as qualification


class Definition(unittest.TestCase):
    def test_actual26_and_original25_qualified_without_replay(self):
        _, counts = subject.inventory()
        self.assertEqual((26, 12), (sum(counts.values()), len(counts)))
        subject.prior25()
        for name in ('WebRuntimeExecutionRetentionTest', 'WebRuntimePendingFailureRetentionTest'):
            self.assertEqual(1, counts['dev.codex.schubert.nk.web.bootstrap.'+name])
        for path in (subject.__file__, qualification.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_generated_counter_projection_cannot_invent_branch0(self):
        raw = subject.prior.red.runner_source(26, 12, target_count=1)
        self.assertIn('if k in counters', raw)
        self.assertIn("set(c)=={'LINE','METHOD','CLASS','BRANCH'}", raw)
        for value in ('systemctl', 'qemu-system', '/opt/schubert-nk/current', '--recover', '--resume'):
            self.assertNotIn(value, raw)


if __name__ == '__main__':
    unittest.main()
