"""Independent literal contract, full generated scope and no mutation check."""
import unittest
from pg2040_fresh_normal_warning_terminal_post import SEALS
from pg2400_retired_current_backup_content import payload, entry, SLOT


class RetiredBackup(unittest.TestCase):
    def test_current_retired_scope_and_independent_content(self):
        raw = payload({k: 'a' * 64 for k in SEALS})
        for literal in ['pg2392-native-stop-v1', 'exactRuntimeEntryRetired',
                        'same_except_runtime', 'prior_equal', 'pg2368-current-resume-full-seal-v1',
                        '91f5484b-9702-4c7c-97f3-dd5110a853f9', '2026-10-13T15:01:53.237266Z',
                        '0.1.0-PG2126/config/templates/api.yml', 'retained_handle',
                        'all24UnchangedTwice', 'nativeMetadataStableTwice',
                        'restorePruneAccepted=False', 'staticConfigAllowlistEntriesVerified']:
            self.assertIn(literal, raw)
        for mutation in ['StartUnit(', 'StopUnit(', 'ReloadUnit(', 'daemon-reload',
                         'pg_restore --clean', 'pg2050']:
            self.assertNotIn(mutation, raw)
        self.assertLess(raw.index('backup_result,listing_bytes = qualify_backup()'),
                        raw.index('finally:', raw.index('native = snapshot()')))
        self.assertEqual(SLOT, entry().__globals__['SLOT'])
        self.assertIs(payload, entry().__globals__['payload'])


if __name__ == '__main__':
    unittest.main()
