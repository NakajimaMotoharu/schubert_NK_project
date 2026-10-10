"""Fixed signed recipient/raw-byte and retained-original joins, no VM writes."""
import ast
import unittest
from unittest.mock import patch
import pg1130_current_failed_capture_v5 as subject


class CaptureTest(unittest.TestCase):
    def test_real_shape_join_fixed_inputs_new_slot_and_no_business_mutation(self):
        retained = {'folder': '/srv/schubert-nk/backup/old', 'startedAt': '2026-10-08T21:33:33Z',
                    'files': {}, 'privateProofSha256': 'a' * 64}
        with patch.object(subject, 'proof', return_value=retained): text = subject.payload()
        ast.parse(text)
        for part in ['failed-capture-v5', 'retired=RETIREMENT',
                     "release/'config/effective/backup-age-recipient'",
                     "artifactSummary['currentArtifactHashes']['config/effective/backup-age-recipient']",
                     "held.project(before['heldWholeMetadata'][1]", 'artifacts.qualify(', 'backup.qualify(']:
            self.assertIn(part, text)
        for part in ['failed-capture-v4', '/credentials/backup-recipient', 'systemctl start', 'systemctl stop']:
            self.assertNotIn(part, text)
        self.assertNotIn('recipient.strip', text)
        self.assertNotIn("'oldOriginalsBackupCredentialsProofsPreserved':True", text)
        self.assertIn("'backupSevenGenerationRetentionVerified':True", text)

    def test_private_proof_refusal_precedes_guest_generation(self):
        with patch.object(subject, 'proof', side_effect=ValueError('untrusted private proof')):
            with self.assertRaises(ValueError): subject.payload()


if __name__ == '__main__': unittest.main()
