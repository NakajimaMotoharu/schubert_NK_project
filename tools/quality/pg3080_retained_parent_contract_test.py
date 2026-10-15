"""Pre-fix counterexample, actual private FD writer and complete retained-only contract."""
import ast
import hashlib
import json
from pathlib import Path
import os
import stat
import tempfile
import unittest
from pyflakes.api import check
import pg3060_browser_resume_sources as failed
import pg3080_retained_parent_resume_sources as fixed
import pg3084_retained_parent_dispatch as dispatch
import pg3086_retained_parent_post as post
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema


class RetainedParent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = fixed.sources()

    def test_pre_fix_cold_guard_rejects_actual_retained_shape(self):
        raw = failed.sources()['pg3060_native_refs.py']
        start = raw.index('    require(set(runtime_before)==')
        end = raw.index("    require(command(['/usr/bin/findmnt'", start)
        block = '\n'.join(line[4:] for line in raw[start:end].splitlines())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / 'unit.d'
            directory.mkdir()
            def require(value):
                if not value:
                    raise ValueError('pre-fix cold-only counterexample')
            with self.assertRaises(ValueError):
                exec(block, {'require': require, 'runtime_before': {str(root): {}, str(directory): {}}, 'runtime_root': root, 'runtime_directory': directory, 'os': os, 'stat': stat})
        refs = self.values['pg3080_native_refs.py']
        self.assertTrue('admit_existing_runtime(runtime_before,runtime_root,runtime_directory,metadata,os.listxattr)' in refs)
        self.assertTrue("runtime.owned_prepare(runtime_before[str(runtime_directory)]['metadata'],dropin)" in refs)

    def test_real_fd_writer_keeps_parent_inode_and_never_replaces_entry(self):
        ns = {}
        exec(self.values['pg3080_runtime_writer.py'], ns)
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'mkdir' for n in ast.walk(ast.parse(self.values['pg3080_runtime_writer.py']))))
        # Synthetic root ownership only; real Linux FD, EXCL, write, force, mode, close and inode.
        original_metadata = ns['metadata']
        def metadata(fd):
            row = original_metadata(fd)
            row[2:4] = [0, 0]
            return row
        ns['metadata'] = metadata
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / 'retained'
            parent.mkdir(mode=0o755)
            fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                before = metadata(fd)
                ns['prepare'](parent, before, b'independent public fixture\n')
                self.assertEqual(before[:6], metadata(fd)[:6])
                target = parent / 'zz-pg3080-once-resume.conf'
                self.assertEqual(b'independent public fixture\n', target.read_bytes())
                self.assertEqual(0o644, stat.S_IMODE(target.stat().st_mode))
                with self.assertRaises(ValueError):
                    ns['prepare'](parent, metadata(fd), b'forbidden overwrite')
                self.assertEqual(b'independent public fixture\n', target.read_bytes())
            finally:
                os.close(fd)

    def test_complete_tree_exact_source_and_post_scopes(self):
        ns = {}
        exec(self.values['pg3080_resume_contract.py'], ns)
        root, directory, target = ns['RUNTIME'], ns['DIRECTORY'], ns['TARGET']
        before = {root: {'metadata': [28, 4000, 0, 0, 0o40755, 3, 60, 10, 10], 'sha256': None}, directory: {'metadata': [28, 4564, 0, 0, 0o40755, 2, 40, 20, 20], 'sha256': None}}
        after = {root: before[root], directory: {'metadata': [28, 4564, 0, 0, 0o40755, 2, 60, 100, 200], 'sha256': None}, target: {'metadata': [28, 6000, 0, 0, 0o100644, 1, 3, 100, 200], 'sha256': hashlib.sha256(b'abc').hexdigest()}}
        self.assertTrue(ns['runtime_tree'](before, after, b'abc', 100, 200))
        for bad in [{root: before[root]}, {**before, target: after[target]}, {}, None]:
            self.assertFalse(ns['runtime_tree'](bad, after, b'abc', 100, 200))
        bad = json.loads(json.dumps(after))
        bad[target]['sha256'] = '0' * 64
        self.assertFalse(ns['runtime_tree'](before, bad, b'abc', 100, 200))
        raw = dispatch.source()
        for old in ['pg3064', 'pg3062', 'pg3060']:
            self.assertTrue(old not in raw, old)
        evidence = json.loads((W / 'pg3078-recovered-browser-full-post-v1/manifest.safe.json').read_bytes())
        seals = {n: evidence['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
        raw = post.payload(seals)
        self.assertEqual(0, check('HASHES={}\nRECEIPT="current"\n' + raw, '<whole corrected post>'))
        for literal in ['zz-pg3080-once-resume.conf', 'pg3084-retained-parent-resume-preparation-v1', 'len(rows) == 24', 'retainedOriginalParent']:
            self.assertTrue(literal in raw, literal)


if __name__ == '__main__':
    unittest.main()
