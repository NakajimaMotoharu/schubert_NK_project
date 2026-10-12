"""Actual entry host FLOCK + no duplicate, emitted child-before-parent phase."""
import ast
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import pg1784_warning_pair_once_handoff as subject
from pg1674_critical_management_gate import management_gate


class Handoff(unittest.TestCase):
    def test_actual_entry_excludes_other_actor_during_ssh(self):
        with tempfile.TemporaryDirectory(prefix='pg1784-gate-')as tmp:
            root=Path(tmp);work=root/'work';private=root/'private';work.mkdir();private.mkdir()
            def run(*args,**kwargs):
                gate=private/'current-management-critical.lock'
                with self.assertRaises(BlockingIOError):
                    with management_gate(gate):self.fail('second actor entered')
                self.assertEqual(subject.SSH+['sudo','-n','python3','-'],args[0])
                self.assertEqual(240,kwargs['timeout'])
                return subprocess.CompletedProcess([],0,b'{"fixture":true}',b'')
            with patch.object(subject,'W',work),patch.object(subject,'P',private),patch.object(subject,'payload',return_value='fixture_only=True\n'),patch.object(subject.subprocess,'run',side_effect=run)as call,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0,subject.main());self.assertEqual(1,call.call_count)
                saved=json.loads((work/subject.SLOT/'manifest.safe.json').read_bytes());self.assertEqual(os.getpid(),saved['hostGate']['pid']);self.assertTrue(saved['oldNormalCloseUnknown']);self.assertFalse(saved['formalAccepted'])
                with self.assertRaises(FileExistsError):subject.main()
                self.assertEqual(1,call.call_count)
            with management_gate(private/'current-management-critical.lock'):pass

    def test_busy_gate_no_ssh(self):
        with tempfile.TemporaryDirectory(prefix='pg1784-busy-')as tmp:
            root=Path(tmp);work=root/'work';private=root/'private';work.mkdir();private.mkdir()
            with management_gate(private/'current-management-critical.lock'),patch.object(subject,'W',work),patch.object(subject,'P',private),patch.object(subject,'payload',return_value='fixture_only=True\n'),patch.object(subject.subprocess,'run')as call:
                with self.assertRaises(BlockingIOError):subject.main()
                call.assert_not_called()

    def test_all_emitted_phase_order_and_no_force(self):
        raw=subject.payload();tree=ast.parse(raw)
        lock=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='owned_lock')
        self.assertIn('actor_for_locks()',ast.get_source_segment(raw,lock))
        body=ast.get_source_segment(raw,next(n for n in tree.body if isinstance(n,ast.Try)and 'terminate(476116' in ast.get_source_segment(raw,n)))
        self.assertLess(body.index('terminate(476116'),body.index('CHILD_REAPED=True'));self.assertLess(body.index('CHILD_REAPED=True'),body.index('terminate(476087'))
        self.assertIn('reserve(pid);signal.pidfd_send_signal(fd,signal.SIGTERM',raw)
        self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr=='SIGKILL'for n in ast.walk(tree)))
        self.assertFalse('pg_terminate_backend' in raw)
        self.assertFalse('reset-failed' in raw)


if __name__=='__main__':unittest.main()
