import re
import unittest
import pg5272_cleanup_factory_selected as role


class CleanupScope(unittest.TestCase):
    def test_related25_cases_and_new_suites_explicit(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RELATED:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'CleanupExpiryExecutionTest':1,'CleanupMaintenanceWorkTest':4,
            'CleanupNativePreflightTest':4,'MaintenanceFileLockTest':9,'TransferCleanupTest':6,
            'TransferCleanupFailureTest':1})
        self.assertEqual(sum(actual.values()),25)
        self.assertEqual(set(role.RELATED)-set(role.previous.extra_suites()),set(role.RELATED))
        self.assertEqual(len(role.extra_suites()),80)

    def test_six_semantic_fifteen_bounded_debug_families(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),37)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),81)


if __name__=='__main__':unittest.main()
