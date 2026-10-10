"""Independent private proof closure/digest/security fixtures; no VM mutation."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pg1129_retired_backup_proof as subject


class ProofTest(unittest.TestCase):
    def fixture(self, root):
        bundle = root / 'bundle'
        bundle.mkdir(mode=0o700)
        files = {}
        for name in sorted(subject.NAMES):
            raw = b'{"startedAt":"2026-10-08T21:33:33.494486Z"}\n' if name == 'MANIFEST.json' else b'independent-original-byte'
            p = bundle / name
            p.write_bytes(raw)
            p.chmod(0o600)
            files[name] = {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                           'originalMetadata': [1, 2, 0, 0, 33152, 1, len(raw), 3, 4]}
        doc = {'files': files, 'sourceIdentityUnchanged': True,
               'currentBackupVmDbModified': False, 'rawOutsideGit': True,
               'originalPath': '/srv/schubert-nk/backup/independent-old'}
        raw = json.dumps(doc).encode()
        (root / 'manifest.private.json').write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def test_original_digests_metadata_and_no_raw_return(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            digest = self.fixture(root)
            with patch.object(subject, 'ROOT', root), patch.object(subject, 'SHA', digest):
                result = subject.proof()
            self.assertEqual(set(result), {'folder', 'startedAt', 'files', 'privateProofSha256'})
            self.assertEqual(result['startedAt'], '2026-10-08T21:33:33.494486Z')
            self.assertEqual(result['privateProofSha256'], digest)
            self.assertEqual(set(result['files']), subject.NAMES)
            self.assertNotIn('independent-original-byte', json.dumps(result))

    def test_pin_digest_missing_link_permissions_and_hardlink_refused(self):
        for fault in ['pin', 'digest', 'missing', 'symlink', 'mode', 'hardlink']:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); digest = self.fixture(root)
                p = root / 'bundle/config.tar'
                if fault == 'pin': digest = '0' * 64
                if fault == 'digest': p.write_bytes(b'changed')
                if fault == 'missing': p.unlink()
                if fault == 'symlink':
                    p.unlink(); p.symlink_to(root / 'bundle/schubert_nk.dump')
                if fault == 'mode': p.chmod(0o644)
                if fault == 'hardlink': os.link(p, root / 'additional-link')
                with patch.object(subject, 'ROOT', root), patch.object(subject, 'SHA', digest):
                    with self.assertRaises((ValueError, FileNotFoundError)): subject.proof()


if __name__ == '__main__': unittest.main()
