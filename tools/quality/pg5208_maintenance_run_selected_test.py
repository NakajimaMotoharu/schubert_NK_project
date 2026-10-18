import re
import unittest
import pg5208_maintenance_run_selected as role


class MaintenanceRunScope(unittest.TestCase):
    def test_all_four_independent_suites_exact63(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RUNS:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'MaintenanceRunFilesTest':39,'MaintenanceRecordsTest':8,
            'MaintenanceRetirementRecordsTest':8,'RunReferenceRepositoryTest':8})
        self.assertEqual(sum(actual.values()),63)
        self.assertEqual(len(role.extra_suites()),58)

    def test_semantic_and_nested_boundaries_explicit(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),15)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),28)
        self.assertIn(role.PREFIX+'MaintenanceRunFiles$Session.class',role.selected.EXTRA_CHANGED)

    def test_only_declared_tempdir_invocations_can_be_expected(self):
        source='@Test void one(@TempDir Path temporary) {} @Test void two() {}'
        self.assertEqual(role.selected.expected_invocations(['one','two'],{'one(Path)':'one'},source),
                         ['one(Path)','two'])
        for aliases in ({'one(String)':'one'},{'absent(Path)':'absent'},
                        {'one(Path)':'one','other(Path)':'one'},{'two(Path)':'two'}):
            with self.assertRaises(ValueError):role.selected.expected_invocations(['one','two'],aliases,source)


if __name__=='__main__':unittest.main()
