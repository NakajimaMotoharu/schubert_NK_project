import unittest
import pg5156_native_coverage_selected as role


class BootstrapScope(unittest.TestCase):
    def test_actual_all_bootstrap_cases_and_fixed_storage_root_union(self):
        suites=role.bootstrap_suites()
        self.assertEqual(len(suites),42)
        self.assertEqual(set(suites.values()),{'bootstrap'})
        for name in ('NativeCoverageExportTest','FixedNativeCoverageTerminalTest','TerminalNativeCoverageProfileTest'):
            self.assertIn('dev.codex.schubert.nk.bootstrap.'+name,suites)
        combined={**role.selected.SUITES,**role.selected.PENDING_SUITES,
           'dev.codex.schubert.nk.batch.file.RootEntryRejectionTest':'batch',
           **role.selected.storage_suites(),**suites}
        self.assertEqual(len(combined),73)
        command=role.selected.commands_for(['MAVEN'],combined)
        self.assertIn('-Dtest='+','.join(combined),command[1])
        self.assertEqual(len(command),2)


if __name__=='__main__':unittest.main()
