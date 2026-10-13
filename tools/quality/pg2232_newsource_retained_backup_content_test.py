import unittest
from pg2232_newsource_retained_backup_content import payload


class RetainedBackup(unittest.TestCase):
    def test_independent_ss_bytes_db_handles_and_full_current_scope(self):
        s=payload()
        for value in ['02bddddf-9cd3-4668-9d67-7561232fc4e4','2026-10-13T06:29:34.698736Z',
          '0.1.0-PG2126/config/templates/api.yml','pg2232-newsource-retained-backup-content-v1',
          'ordinaryPgRestoreListExit=0','backupReplay0=True','restorePruneIntentAccepted=False',
          'fixed_read(', 'oracle.verify(',"first==before['current'] and first==snapshot()"]:
            self.assertIn(value,s)
        self.assertNotIn('0.1.0-PG1638/config/templates/api.yml',s)
        self.assertNotIn('pg_dump',s)


if __name__=='__main__':unittest.main()
