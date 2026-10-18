"""Exact current recovery, independent race/ref-pipe negatives; no signals or VM operations."""
import ast
import copy
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from pyflakes.api import check, checkPath
import pg5096_retained_pair_once_recovery as recovery


class CurrentRecovery(unittest.TestCase):
    def test_complete_factory_exact_order_and_raw_freshproof_before_signal(self):
        raw = recovery.payload()
        self.assertEqual(0, check(raw, '<all current recovery globals>'))
        self.assertTrue('f0496ff80babbe6aa7a1926193739436a8170c3d22c835dd205cc749e85cc1db' in raw)
        self.assertLess(raw.index("private('fresh-complete.private'"), raw.index('terminate(927536'))
        self.assertLess(raw.index('terminate(927536'), raw.index('terminate(927504'))
        self.assertLess(raw.index('terminate(927504'), raw.index("private('post.private.json'"))
        for text in ('reaped(927536, 31055311)', 'reaped(927504, 31055084)',
                     'CURRENT_ACTOR = remaining_actor', 'owned_lock = free_lock',
                     'parent_after_ref', "'oldCloseUnknown': True", "'fullIndependentPostPending': True"):
            self.assertTrue(text in raw, text)
        for text in ('signal.SIGKILL', 'StartUnit(', 'StopUnit(', 'pg_terminate_backend'):
            self.assertTrue(text not in raw, text)
        for path in (recovery.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_same_real_prerequisite_negative_foreign_failed_and_unknown(self):
        real = Path.read_bytes
        location = recovery.W / recovery.proof.SLOT / 'manifest.safe.json'
        original = json.loads(real(location))
        self.assertEqual(original['result']['proofSha256'], recovery.prerequisite())
        for key, invalid in [('actualExit', 1), ('actualExit', None), ('actualExit', False), ('source', 'foreign')]:
            changed = {**original, key: invalid}
            def read(path):
                return json.dumps(changed).encode() if path == location else real(path)
            with self.subTest(key=key), patch.object(Path, 'read_bytes', read), self.assertRaises(ValueError):
                recovery.prerequisite()
        changed = copy.deepcopy(original)
        changed['result']['signals0'] = False
        with patch.object(Path, 'read_bytes', lambda path: json.dumps(changed).encode() if path == location else real(path)):
            with self.assertRaises(ValueError):
                recovery.prerequisite()

    def test_original_snapshot_preserved_except_dynamic_owner_for_known_locks(self):
        defs = lambda raw: {n.name: ast.dump(n, include_attributes=False)
                            for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.FunctionDef)}
        old, new = defs(recovery.proof.payload()), defs(recovery.payload())
        for name in ('snapshot', 'fresh_current_parent', 'native_reference', 'complete_configuration', 'refs_actor', 'pair'):
            self.assertEqual(old[name], new[name], name)

    def test_pidfd_race_refuses_and_reservation_failure_never_sends(self):
        calls = []
        count = iter([{'generation': 1}, {'generation': 2}])
        with self.assertRaises(ValueError):
            recovery.terminate(1, 2, lambda p, t: next(count), lambda p, v: calls.append('reserve'),
                               lambda p: 9, lambda fd: calls.append('send'), lambda fd: True,
                               lambda fd: calls.append('close'))
        self.assertEqual(['close'], calls)
        calls.clear()
        def refuse(pid, value):
            calls.append('reserve')
            raise FileExistsError('already reserved')
        with self.assertRaises(FileExistsError):
            recovery.terminate(1, 2, lambda p,t: {'generation':1}, refuse, lambda p:9,
                               lambda fd:calls.append('send'),lambda fd:True,lambda fd:calls.append('close'))
        self.assertEqual(['reserve', 'close'], calls)

    def test_after_ref_only_known_pipe_descriptors_may_disappear(self):
        parent, _, _ = recovery.proof.proof.observation()
        pipe = next(n for n,v in parent['fds'].items() if v['target'].startswith('pipe:['))
        pipes = {parent['fds'][pipe]['target'], 'pipe:[literal-second]'}
        remaining = copy.deepcopy(parent)
        del remaining['fds'][pipe]
        self.assertTrue(recovery.parent_after_ref(parent, remaining, pipes))
        other = next(n for n,v in remaining['fds'].items() if v['target'] not in pipes)
        del remaining['fds'][other]
        with self.assertRaises(ValueError):
            recovery.parent_after_ref(parent, remaining, pipes)
        remaining = copy.deepcopy(parent)
        remaining['fds']['foreign'] = copy.deepcopy(parent['fds'][pipe])
        with self.assertRaises(ValueError):
            recovery.parent_after_ref(parent, remaining, pipes)


if __name__ == '__main__':
    unittest.main()
