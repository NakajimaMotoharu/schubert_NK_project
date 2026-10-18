"""Independent literal reactor/order expectations; no Maven or VM invocation."""
import unittest
import pg5120_root_elf_selected as role


class SelectedCommandsTest(unittest.TestCase):
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
        self.assertEqual(role.BUILT, ('protocol', 'storage', 'bootstrap', 'batch'))


if __name__ == '__main__':
    unittest.main()
