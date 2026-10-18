import re
import unittest
import pg5192_durable_worker_selected as role


class DurableWorkerScope(unittest.TestCase):
    def test_four_existing_independent_suites_exact42(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.WORKERS:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'DurableRecordFilesTest':12,'BackupWorkerRequestFilesTest':10,
            'CleanupWorkerRequestFilesTest':13,'MorningBackupRequestPublicationTest':7})
        self.assertEqual(sum(actual.values()),42)
        self.assertEqual(len(role.extra_suites()),54)

    def test_only_four_declared_outers_and_bounded_nested_debug(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),13)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),14)
        self.assertIn(role.PREFIX+'DurableRecordFiles.class',role.selected.EXTRA_CHANGED)
        self.assertIn(role.PREFIX+'MorningBackupRequestPublication.class',role.selected.EXTRA_CHANGED)


if __name__=='__main__':unittest.main()
