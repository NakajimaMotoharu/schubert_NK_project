import ast
import unittest
from pg1138_failed_recovery_compile_v3 import source


class ClosureTest(unittest.TestCase):
    def test_all_three_independent_fixture_sources_and_new_v3(self):
        text = source(); ast.parse(text)
        for value in ['pg1134-issued-api-tools-v3', 'pg1138-failed-recovery-frozen-v3',
                      'batch/backup/BackupManifestFixture.java', 'BackupPublicationFixture.java',
                      'BackupArtifactFixture.java', "'-sourcepath', ''", 'pg113[3478]*test.py']:
            self.assertIn(value, text)
        self.assertNotIn('pg1134-issued-api-tools-v2', text)


if __name__ == '__main__': unittest.main()
