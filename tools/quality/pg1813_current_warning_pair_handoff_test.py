"""Actual complete namespace/UUID and retained authority guards before signals."""
import ast
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock
import pg1813_current_warning_pair_handoff as actual
from pg1813_current_warning_pair_handoff import payload,SLOT


class Handoff(unittest.TestCase):
    def test_actual_composed_current_namespace(self):
        raw=payload();tree=ast.parse(raw)
        saved=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ['SAVE','HANDOFF']for t in n.targets)]
        for node in saved[-2:]:self.assertTrue(SLOT in ast.unparse(node))
        self.assertTrue('pg1812-current-warning-pair-proof-v1/proof.private.json'in raw)
        self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in raw)
        self.assertFalse('f1800e'in raw);self.assertFalse('signal.SIGKILL'in raw)
        self.assertTrue('terminate(479219, 8907026, before_child)'in raw)
        self.assertTrue('terminate(479190, 8906867, parent_after_child)'in raw)
        self.assertTrue('actor_for_locks()'in raw)
        self.assertTrue('retained_proof' in raw)

    def exercise_main(self,exit_code):
        with tempfile.TemporaryDirectory(prefix='pg1813-actual-main-')as tmp:
            root=Path(tmp);proof=root/'pg1812-current-warning-pair-proof-v1';proof.mkdir()
            (proof/'manifest.safe.json').write_text(json.dumps({'actualExit':0,'guest':{'proofSha256':actual.PROOF_SHA}}))
            held={'pid':282491};entered=[];event=Mock();event.wait.return_value=True
            @contextlib.contextmanager
            def gate(path,validate_owner,require_completion):
                self.assertEqual(actual.P/'current-management-critical.lock',path)
                self.assertTrue(validate_owner(path));self.assertFalse(require_completion());entered.append(True)
                yield event
                self.assertEqual(exit_code==0,require_completion())
            def run(args,**kwargs):self.assertEqual([True],entered);self.assertTrue(kwargs['timeout']<=240);return Mock(returncode=exit_code,stdout=b'{"actualExit":0}',stderr=b'')
            def command(args,**kwargs):return 'SSC281'if args[:2]==['git','show']else b''
            with patch.object(actual,'W',root),patch.object(actual,'owner',return_value=held),patch.object(actual,'queued_gate',gate),patch.object(actual,'payload',return_value='literal payload'),patch.object(actual.subprocess,'check_output',side_effect=command),patch.object(actual.subprocess,'run',side_effect=run),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(exit_code,actual.main())
            value=json.loads((root/SLOT/'manifest.safe.json').read_bytes());self.assertEqual(exit_code==0,value['queuedSameHostGateAcquired']);self.assertTrue(value['oldNormalCloseUnknown']);self.assertFalse(value['formalAccepted'])
            self.assertEqual(1 if exit_code==0 else 0,event.wait.call_count)

    def test_actual_main_success_gate_handoff(self):self.exercise_main(0)
    def test_actual_main_guard_failure_keeps_old_owner(self):self.exercise_main(1)


if __name__=='__main__':unittest.main()
