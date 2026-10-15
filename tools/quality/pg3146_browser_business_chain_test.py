"""Pure counterexamples for immutable Root -> Browser -> current SQL composition."""
import ast
import copy
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
            # Exercise the multi-prefix composition itself, isolated from each
            # separately tested complete SQL algorithm (never an actual acceptance).
            root['rows']={'phase':1};path.write_text(json.dumps(root));ns['ROOT_SHA']=hashlib.sha256(path.read_bytes()).hexdigest()
            ns['ROOT_ORACLE']="def qualify(old,new,cutoff,done,upper):\n assert new=={'phase':1} and upper=='2026-10-15T02:00:00Z'\n return {'rootPrefixQualified':True}\n"
            ns['PARTIAL_CHAIN']=[{'kind':'LOGIN_ONLY','before':{'phase':1},'after':{'phase':2},'context':{'owner':1,'lower':'2026-10-15T02:00:00Z','upper':'2026-10-15T02:02:00Z'}},{'kind':'AUTH_ADMIN_READ','before':{'phase':2},'after':{'phase':3},'context':{'owner':1,'lower':'2026-10-15T02:03:00Z','upper':'2026-10-15T02:05:00Z'}}]
            ns['PARTIAL_ORACLES']={kind:"def qualify(old,new,owner,lower,upper):\n assert old=={'phase':"+str(index)+"} and new=={'phase':"+str(index+1)+"}\n return {'all24PartialQualified':True,'oldBrowserActualExit':1,'failedCaseNormalized':False}\n"for kind,index in [('LOGIN_ONLY',1),('AUTH_ADMIN_READ',2)]}
            ns['BROWSER_ORACLE']="def qualify(old,new,owner,lower,upper):\n assert old=={'phase':3} and new=={'phase':4}\n return {'all24Qualified':True,'newQuestions':1,'freshAuthSessions':3}\n"
            ns['CHAIN']={'before':{'phase':3},'after':{'phase':4},'context':{'owner':1,'lower':'2026-10-15T02:06:00Z','upper':'2026-10-15T02:08:00Z'}}
            self.assertTrue(ns['qualify']({}, {'phase':4},'cutoff','done','2026-10-15T02:09:00Z')['exactRootBrowserCurrentChain'])
            valid=copy.deepcopy(ns['PARTIAL_CHAIN'])
            for field,bad in [('before',{'phase':99}),('kind','FOREIGN'),('context',{'owner':2,'lower':'2026-10-15T02:03:00Z','upper':'2026-10-15T02:05:00Z'}),('context',{'owner':1,'lower':'2026-10-15T02:01:00Z','upper':'2026-10-15T02:05:00Z'})]:
                ns['PARTIAL_CHAIN']=copy.deepcopy(valid);ns['PARTIAL_CHAIN'][1][field]=bad
                with self.assertRaises((ValueError,AssertionError)):
                    ns['qualify']({}, {'phase':4},'cutoff','done','2026-10-15T02:09:00Z')


if __name__ == '__main__':
    unittest.main()
