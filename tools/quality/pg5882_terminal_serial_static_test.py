import subprocess
import unittest
import pg5882_terminal_serial_static as target


class ExactSerialDecisionTest(unittest.TestCase):
    def test_exact_three_serial_sources_and_sync_unchanged(self):
        for path in target.MODIFIED:
            before=subprocess.check_output(['git','show','0f572da66c9e3f0818cddb5bf679e7b8bc0f47da:'+path],cwd=target.engine.ROOT,text=True)
            self.assertEqual((target.engine.ROOT/path).read_text(),target.expected_source(path,before))
        sync='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/SyncRequestConsumers.java'
        self.assertEqual(subprocess.check_output(['git','show','0f572da66c9e3f0818cddb5bf679e7b8bc0f47da:'+sync],cwd=target.engine.ROOT),(target.engine.ROOT/sync).read_bytes())
        self.assertNotIn('failIfNoTests=false',target.runner_source())
        self.assertIn("expected_counts=Counter(old['ruleCounts'])",target.runner_source())


if __name__=='__main__':unittest.main()
