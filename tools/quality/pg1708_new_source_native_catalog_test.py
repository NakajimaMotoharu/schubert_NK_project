"""Independent PID1 literal fixtures, original-root time/identity bounds."""
import copy
import unittest
from pg1708_new_source_native_catalog import backup_window,catalog_source


class BackupJournalTest(unittest.TestCase):
    def test_genuine_fixed_roles_and_foreign_failed_missing_boundary_rejected(self):
        base={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0',
              '_COMM':'systemd','UNIT':'schubert-nk-backup.service','INVOCATION_ID':'a'*32,
              '__REALTIME_TIMESTAMP':'1791815000000000'}
        rows=[dict(base,__CURSOR='one',__MONOTONIC_TIMESTAMP='67000000000',MESSAGE_ID='7d4958e842da4a758f6c1cdc7b36dcc5',JOB_ID='106999',JOB_TYPE='start'),
              dict(base,__CURSOR='two',__MONOTONIC_TIMESTAMP='67000010000',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='106999',JOB_TYPE='start',JOB_RESULT='done'),
              dict(base,__CURSOR='three',__MONOTONIC_TIMESTAMP='67000020000',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448'),
              dict(base,__CURSOR='four',__MONOTONIC_TIMESTAMP='67000030000',MESSAGE_ID='9d1aaa27d60140bd96365438aad20286',JOB_ID='107000',JOB_TYPE='stop',JOB_RESULT='done')]
        self.assertEqual((67000000000,67000020000),backup_window(rows))
        for key,bad in [('_BOOT_ID','foreign'),('_PID','2'),('_UID','999'),('_COMM','java'),('UNIT','other'),
                        ('INVOCATION_ID',None),('__CURSOR','two'),('__MONOTONIC_TIMESTAMP','66941284514'),
                        ('__REALTIME_TIMESTAMP',None),('JOB_RESULT','failed'),('JOB_ID','107000'),('JOB_TYPE','stop')]:
            changed=copy.deepcopy(rows);changed[0][key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):backup_window(changed)
        for bad in [None,[],rows[:-1],rows+[rows[0]]]:
            with self.subTest(rows=bad),self.assertRaises(ValueError):backup_window(bad)
        raw=catalog_source()
        self.assertIn('len(old)==14',raw)
        self.assertIn('pg1699-new-current-ordinary-once-v1',raw)
        self.assertIn('set(excluded)==set(old)-',raw)
        self.assertNotIn('INVOCATION_ID=1c085a5e6e874ba1b0d647c92ab3c34c',raw)


if __name__=='__main__':unittest.main()
