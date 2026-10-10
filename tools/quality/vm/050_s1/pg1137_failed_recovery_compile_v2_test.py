import ast
import unittest
from pg1137_failed_recovery_compile_v2 import source
from pg1134_failed_recovery_sources import java_files


class CompileTest(unittest.TestCase):
    def test_explicit_fixture_independent_dependencies_and_new_output(self):
        raw = source(); ast.parse(raw)
        for part in ['pg1134-issued-api-tools-v2', 'pg1137-failed-recovery-frozen-v2',
                     'BackupPublicationFixture.java', 'BackupArtifactFixture.java',
                     "'-sourcepath', ''", 'junit-jupiter-api/5.13.4', 'org/opentest4j']:
            self.assertIn(part, raw)
        parent = java_files()['Pg1134SingleApiRecovery.java']
        self.assertIn('import dev.codex.schubert.nk.batch.file.Pg1134SingleApiIntent;', parent)
        self.assertIn('import dev.codex.schubert.nk.batch.file.Pg1134IssuedApiRecovery;', parent)


if __name__ == '__main__': unittest.main()
