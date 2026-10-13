"""Independent source boundary, no Backup/restore action, full current post retained."""
import unittest
from pg2064_current_retained_backup_content import payload
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Backup(unittest.TestCase):
    def test_current_scope_and_archived_template_are_distinct(self):
        raw=payload({n:'a'*64 for n in SEALS})
        for marker in ['def qualify_backup','0.1.0-PG1638/config/templates/api.yml','--list','independentRetainedBackupSummary','same_except_runtime','all24UnchangedTwice','manager.UnrefUnit(u)','bus.close()']:
            self.assertTrue(marker in raw,marker)
        self.assertLess(raw.index('backup_result,listing_bytes = qualify_backup()'),raw.index('finally:',raw.index('native = snapshot()')))
        self.assertFalse("'systemctl', 'start'"in raw)


if __name__=='__main__':unittest.main()
