"""Explicit independent currentrun/cutoff/root oracle; no runtime mutation."""
import unittest
from pg2288_current_run_backup_content import payload,entry,SLOT
from pg2040_fresh_normal_warning_terminal_post import SEALS


class BackupContent(unittest.TestCase):
    def test_full_current_scope_current_run_and_all_required_content(self):
        raw=payload({k:'a'*64 for k in SEALS})
        for literal in ['pg2274-current-signed-owned-stop-tools-v1','pg2274-native-stop-v1','91f5484b-9702-4c7c-97f3-dd5110a853f9','2026-10-13T15:01:53.237266Z','0.1.0-PG2126/config/templates/api.yml','retained_handle','independentCurrentRunBackupSummary','staticConfigAllowlistEntriesVerified','allClientAdvisoryFlock0','restorePruneIntentAccepted=False']:
            self.assertIn(literal,raw)
        self.assertNotIn('4148e3e8-f107-431a-ab27-d6e6d1f1772e',raw)
        self.assertNotIn('pg2274-newboot-owned-stop-tools-v1',raw)
        self.assertNotIn('StopUnit(',raw)
        self.assertNotIn('StartUnit(',raw)
        self.assertLess(raw.index('backup_result,listing_bytes = qualify_backup()'),raw.index('finally:',raw.index('native = snapshot()')))
        self.assertEqual(SLOT,entry().__globals__['SLOT'])
        self.assertIs(payload,entry().__globals__['payload'])


if __name__=='__main__':unittest.main()
