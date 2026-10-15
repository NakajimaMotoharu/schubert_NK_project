"""Pure counterexamples for immutable Root -> Browser -> current SQL composition."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
import pg3146_browser_business_full_seal as seal
from pg3136_browser_rows_oracle_test import fixture


class BrowserChain(unittest.TestCase):
    def test_composition_reads_original_root_and_rejects_each_broken_join(self):
        before, after = fixture()
        chain = {'before': before, 'after': after, 'context': {'owner': 1, 'lower': '2026-10-15T02:00:00Z', 'upper': '2026-10-15T02:02:00Z'}}
        root = {'source': 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25', 'manifestSha256': '37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863', 'rows': before}
        # Isolate composition from the separately tested full Root SQL algorithm.
        prefix = "def qualify(old,new,cutoff,done,upper):\n assert old=={'independentPrefix':True} and len(new)==24 and upper=='2026-10-15T02:00:00Z'\n return {'rootPrefixQualified':True}\n"
        raw = seal.compose('ORACLE=' + repr(prefix) + '\nSLOT="pg3134-browser-resume-full-seal-v1"\n', chain, 'a' * 64)
        oracle = next(ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ORACLE' for t in n.targets))
        self.assertTrue('/pg3134-browser-resume-full-seal-v1/before.private.json' in oracle)
        self.assertFalse('/pg3146-browser-business-full-seal-v1/before.private.json' in oracle)
        ns = {}; exec(compile(oracle, '<pure composite SQL chain>', 'exec'), ns)
        with tempfile.TemporaryDirectory(prefix='pg3146-chain-') as directory:
            path = Path(directory) / 'root.private.json'; path.write_text(json.dumps(root)); path.chmod(0o600)
            ns['ROOT_SHA'] = hashlib.sha256(path.read_bytes()).hexdigest()
            requested = []
            def lookup(name):
                requested.append(name); return path
            ns['pathlib'] = types.SimpleNamespace(Path=lookup)
            real_stat = path.lstat()
            fake_stat = types.SimpleNamespace(st_mode=real_stat.st_mode, st_uid=0, st_gid=0, st_nlink=1)
            class RootFile:
                def lstat(self):return fake_stat
                def read_bytes(self):return path.read_bytes()
                def __fspath__(self):return str(path)
            ns['pathlib'] = types.SimpleNamespace(Path=lambda name: (requested.append(name), RootFile())[1])
            result = ns['qualify']({'independentPrefix': True}, after, 'cutoff', 'done', '2026-10-15T02:03:00Z')
            self.assertTrue(result['rootPrefixQualified'] and result['browserAll24Qualified'] and result['exactRootBrowserCurrentChain'])
            self.assertEqual(['/var/lib/pgpt-s1-preservation/pg3134-browser-resume-full-seal-v1/before.private.json'], requested)
            for altered in [{}, {**after, 'extra': []}]:
                with self.assertRaises(ValueError):
                    ns['qualify']({'independentPrefix': True}, altered, 'cutoff', 'done', '2026-10-15T02:03:00Z')
            with self.assertRaises(ValueError):
                ns['qualify']({'independentPrefix': True}, after, 'cutoff', 'done', '2026-10-15T02:01:00Z')
            ns['ROOT_SHA'] = 'b' * 64
            with self.assertRaises(ValueError):
                ns['qualify']({'independentPrefix': True}, after, 'cutoff', 'done', '2026-10-15T02:03:00Z')


if __name__ == '__main__':
    unittest.main()
