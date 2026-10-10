"""Immutable dual source closure, current profile and distinct v3 slot."""
import ast
import unittest
from pg1124_current_failed_capture_v3 import payload


class CaptureTest(unittest.TestCase):
    def test_actual_old_new_source_paths_and_external_bom(self):
        text=payload();ast.parse(text)
        for value in ['failed-capture-v3','0.1.0-PG932','0.1.0-PG1068',
                      "artifacts.qualify(baseline['artifacts'],original,now,",
                      "artifactSummary['currentArtifactHashes']['config/effective/backup-profile.json']",
                      "'dualSourceScopesVerified':True"]:
            self.assertTrue(value in text)
        self.assertFalse('failed-capture-v1' in text or 'failed-capture-v2' in text)
        self.assertFalse('hashlib.sha256((release/name).read_bytes()).hexdigest()==digest' in text)
        self.assertFalse('systemctl start' in text or 'systemctl stop' in text)


if __name__=='__main__':unittest.main()
