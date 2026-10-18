import re
import unittest
import pg5216_root_credential_selected as role


class RootCredentialScope(unittest.TestCase):
    def test_three_existing_independent_suites_exact25(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.CREDENTIALS:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'RootReleaseApprovalReaderTest':8,'RootServiceCredentialSourceTest':3,
                                'RootBatchCredentialReaderTest':14})
        self.assertEqual(sum(actual.values()),25)
        self.assertEqual(len(role.extra_suites()),61)

    def test_only_three_outers_and_eight_explicit_nested_candidates_added(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),18)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),36)
        self.assertIn(role.PREFIX+'RootServiceCredentialSource.class',role.selected.EXTRA_CHANGED)


if __name__=='__main__':unittest.main()
