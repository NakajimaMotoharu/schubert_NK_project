"""Actual main slot + one fixed SSH + failed/oldslot no replay, isolated fixture."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import pg1782_warning_live_peer_proof_direct as subject


class Entry(unittest.TestCase):
    def test_real_entry_writes_only_new_fixed_slot_and_single_call(self):
        with tempfile.TemporaryDirectory(prefix='pg1782-entry-')as tmp:
            root=Path(tmp);(root/'pg1766-next-day-independent-candidates-v1').mkdir()
            result=subprocess.CompletedProcess([],0,b'{"fixture":true}',b'')
            with patch.object(subject,'W',root),patch.object(subject,'payload',return_value='fixture_only=True\n'),patch.object(subject.subprocess,'run',return_value=result)as run,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0,subject.main());self.assertEqual(1,run.call_count)
                self.assertEqual(subject.SSH+['sudo','-n','python3','-'],run.call_args.args[0]);self.assertEqual(90,run.call_args.kwargs['timeout'])
                self.assertEqual(b'fixture_only=True\n',run.call_args.kwargs['input'])
                saved=json.loads((root/subject.SLOT/'manifest.safe.json').read_bytes());self.assertFalse(saved['wholeAccepted']);self.assertTrue(saved['signals0'])
                with self.assertRaises(FileExistsError):subject.main()
                self.assertEqual(1,run.call_count)
                self.assertEqual([],list((root/'pg1766-next-day-independent-candidates-v1').iterdir()))

    def test_failed_command_never_parses_stdout_as_success(self):
        with tempfile.TemporaryDirectory(prefix='pg1782-fail-')as tmp:
            result=subprocess.CompletedProcess([],1,b'not json',b'fixture error')
            with patch.object(subject,'W',Path(tmp)),patch.object(subject,'payload',return_value='fixture_only=True\n'),patch.object(subject.subprocess,'run',return_value=result),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(1,subject.main())
            saved=json.loads((Path(tmp)/subject.SLOT/'manifest.safe.json').read_bytes());self.assertNotIn('guest',saved);self.assertEqual(1,saved['actualExit'])


if __name__=='__main__':unittest.main()
