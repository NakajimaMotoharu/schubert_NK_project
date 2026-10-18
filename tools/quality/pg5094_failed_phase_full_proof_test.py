"""Real diagnostic entry mock: refusal, one-shot raw-first evidence and no unlock/relock."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg5094_failed_phase_full_proof as entry


class FailedPhaseEntry(unittest.TestCase):
    def test_full_source_static_and_distinct_namespace(self):
        raw = entry.payload()
        self.assertEqual(0, check(raw, '<same frozen scope readonly>'))
        self.assertTrue('SLOT=' + repr(entry.SLOT) in raw)
        self.assertTrue('SLOT=' + repr(entry.proof.SLOT) not in raw)
        self.assertEqual(0, checkPath(entry.__file__))
        self.assertEqual(0, checkPath(__file__))

    def test_foreign_phase_refuses_before_ssh(self):
        with patch.object(entry, 'fixed_failure', side_effect=ValueError('foreign')), patch.object(entry.subprocess, 'run') as ssh:
            with self.assertRaisesRegex(ValueError, 'foreign'):
                entry.main()
            ssh.assert_not_called()

    def test_foreign_original_owner_refuses_before_ssh(self):
        with patch.object(entry, 'fixed_failure'), patch.object(entry, 'host_owner', side_effect=ValueError('foreign owner')), patch.object(entry.subprocess, 'run') as ssh:
            with self.assertRaisesRegex(ValueError, 'foreign owner'):
                entry.main()
            ssh.assert_not_called()

    def test_entry_once_raw_first_original_owner_before_after_no_general_gate(self):
        with tempfile.TemporaryDirectory(prefix='pg5094-entry-') as directory:
            root = Path(directory)
            result = subprocess.CompletedProcess([], 0, b'{"actualExit":0,"signals0":true}', b'')
            with (patch.object(entry, 'W', root), patch.object(entry, 'fixed_failure'),
                  patch.object(entry, 'host_owner') as owner, patch.object(entry, 'authenticate_host'),
                  patch.object(entry, 'payload', return_value='print("readonly")\n'),
                  patch.object(entry.subprocess, 'run', return_value=result) as ssh,
                  contextlib.redirect_stdout(io.StringIO())):
                self.assertEqual(0, entry.main())
                self.assertEqual(2, owner.call_count)
                self.assertEqual(1, ssh.call_count)
                self.assertEqual(entry.SSH + ['sudo', '-n', 'python3', '-B', '-'], ssh.call_args.args[0])
                saved = root / entry.SLOT
                self.assertEqual(result.stdout, (saved / 'stdout.private.log').read_bytes())
                self.assertIs(json.loads((saved / 'manifest.safe.json').read_bytes())['signals0'], True)
                with self.assertRaises(FileExistsError):
                    entry.main()
                self.assertEqual(1, ssh.call_count)


if __name__ == '__main__':
    unittest.main()
