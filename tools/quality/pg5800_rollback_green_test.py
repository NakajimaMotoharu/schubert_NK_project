import unittest
from pathlib import Path
from unittest.mock import patch
import pg5800_rollback_green as target


class ExplicitRollbackInventoryTest(unittest.TestCase):
    def test_tempdir_injection_and_timeout_not_parameterized_aliases(self):
        with patch.object(Path,'read_text',return_value='@Test @Timeout(20) void ordinary(@TempDir Path root) {}'):
            self.assertEqual({'ordinary'},target.source_test_names(Path('synthetic')))
        for raw in('@ParameterizedTest void a() {}','@Test void a() {} @Test void a() {}','@TestFactory void a() {}','@Disabled @Test void a() {}'):
            with patch.object(Path,'read_text',return_value=raw):
                with self.assertRaises(ValueError):target.source_test_names(Path('synthetic'))

    def test_exact54_and_six_no_tests_guards_unchanged(self):
        from pg5540_snapshot_scratch_selected import ROOT
        total=suites=0
        for module,classes in target.CASES.items():
            for cls in classes:
                path=ROOT/('src/schubert-nk-'+module+'/src/test/java')/('dev/codex/schubert/nk/'+cls.replace('.','/')+'.java')
                self.assertEqual(target.COUNTS[cls.rsplit('.',1)[1]],len(target.source_test_names(path)))
                total+=len(target.source_test_names(path));suites+=1
        self.assertEqual((54,15),(total,suites))
        value=target.runner_source()
        self.assertIn('len(physical)==1665',value)
        self.assertNotIn('failIfNoTests=false',value)
        self.assertNotIn('lan_server',value)
        self.assertNotIn('systemctl',value)


if __name__=='__main__':unittest.main()
