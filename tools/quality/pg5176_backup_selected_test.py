import re
import unittest
import pg5176_backup_selected as role


class BackupScope(unittest.TestCase):
    def test_all_five_backup_suites_have_exact_literal_case_counts_not_helpers(self):
        counts={}
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        for name in role.BACKUP:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),raw.count('@Test'))
            self.assertEqual(len(set(methods)),len(methods))
            counts[name.rpartition('.')[2]]=len(methods)
        self.assertEqual(counts,{'BackupArtifactVerifierTest':18,'BackupManifestPublisherTest':16,
          'BackupManifestReaderTest':24,'BackupManifestCodecTest':8,'BackupManifestValuesTest':8})
        self.assertEqual(sum(counts.values()),74)
        self.assertEqual(len(role.extra_suites()),47)

    def test_extra_source_changes_and_debug_only_candidates_are_bounded(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),6)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),6)
        self.assertIn('batch:dev/codex/schubert/nk/batch/file/BackupArtifactVerifier.class',role.selected.EXTRA_CHANGED)


if __name__=='__main__':unittest.main()
