"""Independent PID1 literals: current Backup GC is not a success/source proof."""
import copy
import unittest
from pg1586_current_native_catalog_v2 import backup_window,catalog_source

class BackupGenerationTest(unittest.TestCase):
    def test_genuine_binding_all_fields_and_rejection(self):
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-backup.service','INVOCATION_ID':'d479dcdf4d784f898979844b130dd450','__REALTIME_TIMESTAMP':'1791779886595819'}
        rows=[dict(common,__CURSOR='fixture-start',__MONOTONIC_TIMESTAMP='32060797641',MESSAGE_ID='7d4958e842da4a758f6c1cdc7b36dcc5',JOB_ID='51019',JOB_TYPE='start'),dict(common,__CURSOR='fixture-done',__MONOTONIC_TIMESTAMP='32061771845',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='51019',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='fixture-success',__MONOTONIC_TIMESTAMP='32062391348',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448'),dict(common,__CURSOR='fixture-stop',__MONOTONIC_TIMESTAMP='32062392052',MESSAGE_ID='9d1aaa27d60140bd96365438aad20286',JOB_ID='51166',JOB_TYPE='stop',JOB_RESULT='done')]
        self.assertEqual(backup_window(rows),(32060797641,32062391348))
        for i,row in enumerate(rows):
            for k in row:
                bad=copy.deepcopy(rows);bad[i][k]='fixture-start'if k=='__CURSOR'and i else ''if k=='__CURSOR'else 'foreign'
                with self.assertRaises(ValueError):backup_window(bad)
        for bad in [None,[],rows[:-1],rows+[rows[0]],[dict(r,JOB_RESULT='timeout')for r in rows],[dict(r,__MONOTONIC_TIMESTAMP='0')for r in rows],[{'MainPID':'0','Result':'success'}]]:
            with self.assertRaises(ValueError):backup_window(bad)
    def test_eight_not_old_seven_oracle_and_exclusions(self):
        raw=catalog_source();self.assertIn("('backup/backup.exec','schubert-nk-backup.service')",raw)
        self.assertIn('start=backup_start;end=backup_end',raw)
        self.assertIn('len(selected)==8',raw);self.assertNotIn('len(selected)==7',raw)
        self.assertIn("require(set(excluded)=={'ordinary-inspector196/",raw)
        self.assertIn('oldSixArchiveUnchanged',raw)

if __name__=='__main__':unittest.main()
