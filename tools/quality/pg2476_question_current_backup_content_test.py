import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema
import pg2476_question_current_backup_content as backup


class CurrentBackup(unittest.TestCase):
    def test_full_independent_current_tuple_and_nonmutating_content_reader(self):
        v=json.loads((W/'pg2464-question-current-owned-post-v1/manifest.safe.json').read_bytes())
        seals={n:v['proofHashes'][n]['sha256']for n in schema.previous.SEALS}
        raw=backup.payload(seals)
        self.assertEqual(0,check('HASHES={}\nRECEIPT="actual"\n'+raw,'<whole current Backup fixture>'))
        for text in ['06236d14-a6f8-4d05-a6ff-49c713cc2647','2026-10-13T21:16:10.125382Z',
                     '0.1.0-PG2428/config/templates/api.yml','qualify_backup()','independentCurrentRunBackupSummary',
                     'ordinaryPgRestoreListExit','pg_restore','restorePruneAccepted=False']:
            self.assertTrue(text in raw,text)
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n,ast.List):
                self.assertFalse({'start','stop','restart','reload','daemon-reload','reset-failed'}&{getattr(v,'value',None)for v in n.elts if isinstance(v,ast.Constant)})
        self.assertEqual(backup.entry().__globals__['SOURCE'],'cdbc07cdf77370d521e64de8b327da7f6752139b')


if __name__=='__main__':unittest.main()
