"""Actual frozen/preflight schema and recursive tar closed inventory, no guest actions."""
import copy
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import pg1377_bootstrap_role_dispatch as p

class Test(unittest.TestCase):
    def setUp(self):
        self.frozen=json.loads((p.W/'pg1375-frozen-v2.safe.json').read_bytes())
        self.guard=json.loads((p.W/'pg1376-bootstrap-role-preflight-v1.safe.json').read_bytes())

    def test_actual_schema_and_negative_types(self):
        expected=self.frozen['fileHashes'];self.assertEqual(expected,p.qualify(self.frozen,self.guard))
        for name,source in (('frozen',self.frozen),('guard',self.guard)):
            for field in ('actualExit','productionSource'):
                for value in (None,False,'0',1,'foreign'):
                    changed=copy.deepcopy(source);changed[field]=value
                    with self.assertRaises(ValueError):p.qualify(changed,self.guard)if name=='frozen'else p.qualify(self.frozen,changed)
        for value in (False,None,0,'true'):
            changed=copy.deepcopy(self.guard);changed['allClientAdvisoryFlock0']=value
            with self.assertRaises(ValueError):p.qualify(self.frozen,changed)
        for name in ('../escape','/absolute','dev/../escape','dev//extra'):
            changed=copy.deepcopy(self.frozen);changed['fileHashes'][name]='a'*64
            with self.assertRaises(ValueError):p.qualify(changed,self.guard)
        compile(p.STAGE,'<actual recursive staging>','exec')
        self.assertTrue('seen==directories|set(FILES)'in p.STAGE)
        self.assertTrue('0.1.0-PG1292'in p.STAGE)
        self.assertTrue('pg1374-bootstrap-role-tools-v2'in p.STAGE)

    def test_actual_tar_shape_from_full_recursive_class_family(self):
        target=p.W/'pg1374-bootstrap-role-tools-v2';expected=set(self.frozen['fileHashes'])|{'payload-sha256.json'}
        with tempfile.TemporaryFile()as stream:
            with tarfile.open(fileobj=stream,mode='w')as archive:archive.add(target,arcname='.',recursive=True)
            stream.seek(0)
            with tarfile.open(fileobj=stream,mode='r:')as archive:
                files=set();dirs=set()
                for node in archive.getmembers():
                    name=str(p.PurePosixPath(node.name));self.assertFalse(node.issym()or node.islnk())
                    if node.isdir():dirs.add(name)
                    else:self.assertTrue(node.isfile());files.add(name)
            self.assertEqual(expected,files)
            parents={'.'}
            for name in self.frozen['fileHashes']:parents.update(str(q)for q in p.PurePosixPath(name).parents)
            self.assertEqual(parents,dirs)

if __name__=='__main__':unittest.main()
