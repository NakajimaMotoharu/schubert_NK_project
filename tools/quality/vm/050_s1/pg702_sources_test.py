"""BOOT702001 independent literal pins and actual isolated transitive imports."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from pg702_sources import python_files, java, refs, native, compile_script, receipt


class Test(unittest.TestCase):
    def test_current_pins_and_old_proof_preservation(self):
        r = refs(); n = native(); j = java(); c = compile_script(); p = receipt()
        for value in (r, n, p): ast.parse(value)
        for literal in ('len(baseline)==21', '==524)', 'pg701-completed-baseline-v1',
                        'bde365dd6ec48fb6c59cd9f8a255cdf664be4a3246283825ba429bb59754038a',
                        "baseline['currentBootstrapProofs']", 'pg664-bootstrap-tools-v1',
                        'pg664-bootstrap-verify-v1', 'pg664-bootstrap-existing-v1',
                        '==121040711116', 'pg696-native-stop-v1'):
            self.assertIn(literal, r)
        for literal in ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f',
                        '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480',
                        '8633b77f-77dc-4a78-88b4-41165f159b43',
                        '2026-10-09T00:43:10.150245Z', 'c6815985-26c5-4f5f-aed0-abc81fa8f71e',
                        '2026-10-09T01:12:17.452418Z'):
            self.assertIn(literal, j)
        self.assertIn('pg682-release-v1', c)
        self.assertIn('$task_work/pg464-code-tools-v2', c)
        self.assertIn("'pg556_parent_receipt.py', 'pg702_parent_receipt.py'", n)
        self.assertIn("prior['actualExit'] == 0 and prior['toolHashes'] == hashes", n)
        self.assertIn("JOB='122726'", p); self.assertIn('START=119288459330', p)
        for old in ('36fe7a0b', 'PG631', 'pg661-completed-baseline', '095f6d1d', '601297d0'):
            self.assertNotIn(old, r + n + j + p + c)

    def test_isolated_import_and_each_missing_required_module(self):
        files = python_files()
        self.assertEqual(len(files), 10)
        for missing in (None, *files.keys()):
            if missing == 'pg702_bootstrap_existing.py': continue
            with self.subTest(missing=missing), tempfile.TemporaryDirectory(prefix='pg702-import-') as directory:
                root = Path(directory)
                for name, raw in {**files, 'dbus.py': '# host-only inert import stub\n'}.items():
                    if name == missing: continue
                    fd = os.open(root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
                    with os.fdopen(fd, 'w') as output: output.write(raw)
                code = 'import sys;sys.path.insert(0,' + repr(directory) + ');import pg702_bootstrap_existing'
                got = subprocess.run([sys.executable, '-I', '-B', '-c', code], capture_output=True)
                if missing is None:
                    self.assertEqual(got.returncode, 0, got.stderr.decode())
                    self.assertEqual(got.stdout + got.stderr, b'')
                else:
                    self.assertNotEqual(got.returncode, 0)
                    self.assertIn(('No module named ' + repr(missing[:-3])).encode(), got.stderr)


if __name__ == '__main__': unittest.main()
