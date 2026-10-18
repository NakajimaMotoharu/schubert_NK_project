import re
import unittest
import pg5224_current_permit_selected as role


class CurrentPermitScope(unittest.TestCase):
    def test_existing_three_suites_exact33(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.PERMIT:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'RootCurrentPermitPreflightTest':6,'StartupPermitFilesTest':15,'RootReleaseAdmissionTest':12})
        self.assertEqual(sum(actual.values()),33)
        self.assertEqual(len(role.extra_suites()),64)

    def test_only_three_outers_and_twelve_explicit_nested_candidates(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),21)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),48)
        self.assertIn(role.PREFIX+'platform/RootReleaseAdmission.class',role.selected.EXTRA_CHANGED)


if __name__=='__main__':unittest.main()
