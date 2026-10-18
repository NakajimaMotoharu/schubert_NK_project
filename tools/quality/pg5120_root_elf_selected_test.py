"""Independent literal reactor/order expectations; no Maven or VM invocation."""
import inspect
import unittest
import pg5120_root_elf_selected as role


class SelectedCommandsTest(unittest.TestCase):
    def test_private_parent_and_native_fixture_child_umasks_are_separate(self):
        self.assertEqual(role.TEST_UMASK, 0o027)
        raw = inspect.getsource(role.main)
        self.assertIn('os.umask(0o077)', raw)
        self.assertIn('umask=TEST_UMASK', raw)
        self.assertIn("'parentUmask': '0077', 'childMavenUmask': '0027'", raw)

    def test_all_six_production_format_only_precedes_selected_pt(self):
        commands = role.commands_for(['MAVEN'])
        self.assertEqual(commands[0], ['MAVEN', '-pl',
            'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch',
            'spotless:check'])
        self.assertNotIn('test', commands[0])
        self.assertEqual(commands[1][1:4], ['-pl',
            'src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch', '-am'])
        self.assertIn('test', commands[1])
        self.assertIn('-Dsurefire.failIfNoSpecifiedTests=false', commands[1])
        self.assertNotIn('program/characterization', ' '.join(map(' '.join, commands)))
        self.assertEqual(len(commands), 2)

    def test_original_and_new_real_suite_names_are_exact(self):
        self.assertEqual(role.SUITES, {
            'dev.codex.schubert.nk.storage.ServiceConfigFilesTest': 'storage',
            'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest': 'bootstrap',
            'dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest': 'batch',
            'dev.codex.schubert.nk.batch.file.RootElfDigestPortTest': 'batch'})
        self.assertEqual(role.BUILT, ('storage', 'bootstrap', 'batch'))

    def test_pending_scope_keeps_all_elf_cases_and_adds_real_wait_and_file_suites(self):
        self.assertEqual(role.PENDING_SUITES, {
            'dev.codex.schubert.nk.batch.file.RootPendingWaitTest': 'batch',
            'dev.codex.schubert.nk.batch.file.RootStartupPendingTest': 'batch',
            'dev.codex.schubert.nk.batch.file.StartupLaunchFilesTest': 'batch'})
        suites = {**role.SUITES, **role.PENDING_SUITES}
        command = role.commands_for(['MAVEN'], suites)
        self.assertEqual(len(suites), 7)
        self.assertEqual(command[0], role.commands_for(['MAVEN'])[0])
        self.assertIn('-Dtest=' + ','.join(suites), command[1])

    def test_factory_scope_uses_all_actual_storage_and_strict_three_compiled_modules(self):
        storage = role.storage_suites()
        self.assertEqual(len(storage), 25)
        self.assertEqual(set(storage.values()), {'storage'})
        for required in ('FactoryResourceScopeTest','OwnedDirectoryFactoryTest','ResourceScopeTest','OwnedTransferDirectoryTest'):
            self.assertIn('dev.codex.schubert.nk.storage.' + required, storage)
        suites = {**role.SUITES, **role.PENDING_SUITES,
                  'dev.codex.schubert.nk.batch.file.RootEntryRejectionTest':'batch', **storage}
        self.assertEqual(len(suites), 32)
        commands = role.commands_for(['MAVEN'], suites)
        self.assertIn('-Dtest=' + ','.join(suites), commands[1])
        self.assertEqual(commands[0], role.commands_for(['MAVEN'])[0])


if __name__ == '__main__':
    unittest.main()
