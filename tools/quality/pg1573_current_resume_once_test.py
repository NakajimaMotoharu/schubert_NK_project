"""One dispatch structure and actual legacy-native copy with independent abc hash."""
import ast
import json
import os
from pathlib import Path
import tempfile
import unittest
from pg1573_current_resume_once import BODY,compose

class OnceTest(unittest.TestCase):
    def test_only_one_start_after_durable_guard_and_unknown_rejected(self):
        h={'pg1572_watch_parent.py':'a'*64,'pg457_stable_actor.py':'b'*64,'pg462_observer_identity.py':'c'*64};s=compose(h)
        self.assertEqual(s.count("'start','--no-block','schubert-nk-morning-controller.service'"),1)
        self.assertLess(s.index("persist('external-start-guard.private.json'"),s.index("'start','--no-block'"))
        self.assertLess(s.index('native_count=preserve_old_native(first)'),s.index("'start','--no-block'"))
        self.assertIn('snapshot()==frozen and watch_identity()==watch',s)
        for bad in [None,{},[],dict(h,extra='d'*64),dict(h,pg1572_watch_parent_py='d'*64)]:
            with self.assertRaises(ValueError):compose(bad)
        for bad in [None,'A'*64,'a'*63]:
            v=dict(h);v['pg1572_watch_parent.py']=bad
            with self.assertRaises(ValueError):compose(v)

    def test_actual_native_copy_keeps_source_and_rejects_wrong_hash(self):
        node=next(n for n in ast.parse(BODY).body if isinstance(n,ast.FunctionDef)and n.name=='preserve_old_native')
        with tempfile.TemporaryDirectory(prefix='pg1573-independent-native-')as name:
            root=Path(name)/'native';root.mkdir();p=root/'legacy.exec';p.write_bytes(b'abc');save=Path(name)/'save';save.mkdir()
            def metadata(path):
                s=path.stat();return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
            def require(value):
                if not value:raise ValueError('native before differs')
            class Paths:
                @staticmethod
                def Path(path):return root if path=='/run/schubert-nk/pt-coverage'else Path(path)
            records={}
            def persist(n,v):records[n]=v
            import hashlib
            env={'pathlib':Paths,'SAVE':save,'require':require,'metadata':metadata,'os':os,'hashlib':hashlib,'persist':persist}
            exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual native preservation>','exec'),env)
            current={'runtime':{'pt-coverage':{str(p):{'metadata':metadata(p),'sha256':'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}}}}
            self.assertEqual(env['preserve_old_native'](current),1);self.assertEqual(p.read_bytes(),b'abc');self.assertEqual((save/'native-before-private/legacy.exec').read_bytes(),b'abc')
            self.assertEqual(records['native-before-manifest.private.json']['legacy.exec']['sha256'],current['runtime']['pt-coverage'][str(p)]['sha256'])
            with self.assertRaises(FileExistsError):env['preserve_old_native'](current)
            second=Path(name)/'other';second.mkdir();env['SAVE']=second;current['runtime']['pt-coverage'][str(p)]['sha256']='0'*64
            with self.assertRaises(ValueError):env['preserve_old_native'](current)
            self.assertEqual(p.read_bytes(),b'abc');self.assertFalse((second/'native-before-private/legacy.exec').exists())
            self.assertNotIn('credential',json.dumps(records))

if __name__=='__main__':unittest.main()
