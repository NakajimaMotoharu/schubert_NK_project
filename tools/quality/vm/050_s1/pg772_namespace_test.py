"""Independent actual threehelper normal and each missing dependency, never Root operation."""
import ast
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from pg772_failure_capture import source,R


def require(value):
    if not value:raise ValueError('literal independent guard refused')


def namespace(missing=None):
    raw=(R/'pg480_backup_refs.py').read_text()
    defs=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name in ('command','metadata','tree')]
    env={'hashlib':hashlib,'stat':stat,'subprocess':subprocess,'require':require}
    if missing is not None:env.pop(missing)
    exec(compile(ast.Module(body=defs,type_ignores=[]),'<literal helpergraph>','exec'),env);return env


class Test(unittest.TestCase):
    def test_payload_has_complete_namespace_and_newonly(self):
        raw=source();tree=ast.parse(raw)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));ast.parse(payload)
        self.assertIn('import ast,hashlib,json,os,pathlib,stat,subprocess,time',payload);self.assertIn('def require(value):',payload)
        self.assertIn('pg772-failure-current758-v1',raw);self.assertNotIn('pg771-failure-current758-v1',raw)
        for value in ('e4093109ab234700b61dd45711126e4e','137240785885',"parent['ExecMainStatus']=='143'",'genuineDoneAccepted'):self.assertIn(value,raw)

    def test_normal_command_tree_then_all_dependency_missing(self):
        env=namespace();command=[sys.executable,'-B','-c',"print('independent literal')"]
        self.assertEqual(b'independent literal\n',env['command'](command))
        with self.assertRaises(ValueError):env['command'](command,1)
        with self.assertRaises(ValueError):env['command']([sys.executable,'-B','-c','raise SystemExit(1)'])
        with tempfile.TemporaryDirectory(prefix='pg772-readonly-')as directory:
            root=Path(directory);fd=os.open(root/'fixture',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b'independent literal');os.close(fd)
            got=env['tree'](root);self.assertEqual(2,len(got));self.assertEqual(hashlib.sha256(b'independent literal').hexdigest(),got[str(root/'fixture')]['sha256'])
            self.assertEqual(0o100600,got[str(root/'fixture')]['metadata'][4])
            for missing in ('require','stat','hashlib'):
                with self.subTest(missing=missing),self.assertRaises(NameError):namespace(missing)['tree'](root)
        with self.assertRaises(NameError):namespace('subprocess')['command'](command)


if __name__=='__main__':unittest.main()
