"""Independent OS fault-oracle checks, not Production expected-value generation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath

FILE = Path(__file__).parent / 'vm/050_s1/pg3216_legacy_negative_observer.py'
SPEC = importlib.util.spec_from_file_location('negative_os_oracle', FILE)
observer = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(observer)


class IndependentWitness(unittest.TestCase):
    def test_complete_namespace_and_separate_fixed_authorities(self):
        self.assertEqual(0, checkPath(str(FILE)))
        self.assertEqual('dd710ec8-bfdf-4157-b445-8073895110d2', observer.BOOT)
        self.assertEqual('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25', observer.SOURCE)
        self.assertEqual(b'PGPT_INVALID_APPROVAL\n', observer.BAD)
        self.assertEqual(['PT-OPS-LFACT00' + str(i) for i in range(1, 8)], observer.IDS)
        with self.assertRaises(ValueError): observer.require(False)

    def test_real_inotify_no_read_then_access_then_mutation_not_interchangeable(self):
        with tempfile.TemporaryDirectory() as directory:
            approval = Path(directory) / 'approval'; credential = Path(directory) / 'credential'
            approval.write_bytes(b'fixed-independent-vector'); credential.write_bytes(b'not-a-secret')
            watch = observer.Watch([approval, credential])
            try:
                self.assertEqual([], watch.read())
                self.assertEqual(b'fixed-independent-vector', approval.read_bytes())
                events = watch.read()
                self.assertTrue(any(p == str(approval) and m & 1 for p, m in events))
                self.assertFalse(any(p == str(credential) for p, m in events))
                self.assertEqual([], watch.read())
                approval.write_bytes(b'mutated')
                self.assertTrue(any(m & 2 for p, m in watch.read()))
                credential.read_bytes()
                self.assertTrue(any(p == str(credential) and m & 1 for p, m in watch.read()))
            finally: watch.close()

    def test_foreign_guest_and_non_root_refuse_before_operation(self):
        with patch.object(observer.os, 'geteuid', return_value=1000):
            with self.assertRaises(ValueError): observer.guard()
        with patch.object(observer.os, 'geteuid', return_value=0), patch.object(observer.Path, 'read_text', return_value='wrong-boot\n'):
            with self.assertRaises(ValueError): observer.guard()

    def test_monitor_barrier_and_bad_read_cannot_be_silently_assumed(self):
        raw = FILE.read_text()
        for literal in ['socket.SO_PEERCRED', "mask & 1", 'events = watch.read()', "len(names) == 25", "'GetUnit'", 'self.process.poll() is None', "'casesPassed'", "'nativeAccepted': False", "before['database']", "before['tree']", "'ExecMainStatus'] == '0'"]:
            self.assertIn(literal, raw)
        for forbidden in ['MorningProcessMain\n', 'signal.SIGKILL', 'systemctl restart', 'getDeclaredMethod', 'setAccessible']:
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
