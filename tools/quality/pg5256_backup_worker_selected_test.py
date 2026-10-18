import re
import unittest
import pg5256_backup_worker_selected as role
import pg5252_startup_view_public as public


class BackupWorkerScope(unittest.TestCase):
    def test_existing35_cases_exact_three_suites(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.BACKUP:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'BackupDatabaseWorkerTest':10,'BackupDatabaseCopyTest':8,'BackupBundlePublisherTest':17})
        self.assertEqual(sum(actual.values()),35)
        self.assertEqual(len(role.extra_suites()),70)

    def test_three_semantic_five_bounded_debug_families(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),28)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),60)

    def test_all_public_case_overrides_preserved_without_new_case_credit(self):
        values=public.revalidated_case_ids()
        self.assertEqual(len(values),15)
        self.assertTrue(all(v['newIndependentCase'] and v['newInThisChange'] is False for v in values.values()))
        self.assertEqual(sum(v['newInThisChange'] for v in public.revalidated_case_ids(view_new=True).values()),8)


if __name__=='__main__':unittest.main()
