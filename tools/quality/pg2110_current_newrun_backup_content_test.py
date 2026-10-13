"""Actual same-source current whole post and independently bound newrun archive/template/handles."""
import unittest
from pg2110_current_newrun_backup_content import payload,entry,SLOT
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Backup(unittest.TestCase):
    def test_actual_complete_scope_and_current_template(self):
        raw=payload({n:'a'*64 for n in SEALS})
        for marker in ['pg2090-native-stop-v1','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','2026-10-13T03:08:18.452473Z','PG1846/config/templates/api.yml','retained_handle','independentNewRunBackupSummary','manager.UnrefUnit(u)','allClientAdvisoryFlock0']:
            self.assertTrue(marker in raw,marker)
        self.assertLess(raw.index('backup_result,listing_bytes = qualify_backup()'),raw.index('finally:',raw.index('native = snapshot()')))
        self.assertEqual(SLOT,entry().__globals__['SLOT']);self.assertIs(payload,entry().__globals__['payload'])


if __name__=='__main__':unittest.main()
