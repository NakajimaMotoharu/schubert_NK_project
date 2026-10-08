"""Immutable archive rebinding, no guest actions."""
import unittest
from pg649_backup_preserve import source


class Binding(unittest.TestCase):
    def test_archive_all_current_files_readonly_and_new_private_slot(self):
        v=source();compile(v,'<current readonly archive>','exec')
        for text in ('pg647-runtime-retirement-v1','9435e98281c0295a9f85d26623d5595191eb849c8c5f1befb82f17ddd3701770',
                     'pg649-prior-eight-backups.private.tar','len(directories)==13 and len(regular)==39 and len(members)==52',
                     "'priorEligibleBundles':8",'os.O_RDONLY|os.O_NOFOLLOW','metadata(p)==v',"'serverMutations':0"):
            self.assertIn(text,v)
        for text in ('pg626-prior-seven-backups', '.unlink(', '.extractall(', 'systemctl', 'daemon-reload'):
            self.assertNotIn(text,v)


if __name__=='__main__':unittest.main()
