import subprocess
import unittest
from pathlib import Path
from pg2346_current_eleven_fd_handoff_v2 import scope,payload


class PublishedScope(unittest.TestCase):
    def test_real_three_documents_and_explicit_negative_boundaries(self):
        paths=['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md']
        for path in paths:
            old=subprocess.check_output(['git','show','origin/main:'+path],text=True)
            self.assertEqual(scope(old),scope(Path(path).read_text()))
            self.assertEqual(scope(old),scope(old+'\nforeign history outside section'))
            for bad in [None,'missing',old.replace('## SSC-284（','## SSC-000（'),old+'\n## SSC-284（duplicate',old.replace('設計公開はこれらやcoverage/PGPT完了の認定ではない。','missing')]:
                with self.assertRaises(ValueError):scope(bad)
            self.assertNotEqual(scope(old),scope(old.replace('親M-A/同peer双方向TCP','foreign authority')))
        self.assertIn('pg2346-current-eleven-fd-handoff-v2',payload())


if __name__=='__main__':unittest.main()
