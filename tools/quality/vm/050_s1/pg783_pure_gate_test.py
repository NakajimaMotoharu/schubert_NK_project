"""Independent repeated callback oracle: actual helper.main reads but never receipt-writes."""
import ast
import copy
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from pg783_sources import helper,java


class Test(unittest.TestCase):
    def test_actual_callback_twice_and_ten_times_is_writefree(self):
        mod=types.ModuleType('pg783_owned');mod.__file__=str(Path(__file__).parent/'pg783_owned.py')
        with patch.dict(sys.modules,{'dbus':types.SimpleNamespace()}):exec(compile(helper(),'<actual existing-only helper>','exec'),mod.__dict__)
        root='/run/schubert-nk/startup';names=[root,root+'/epoch.current',root+'/permit-start.intent',root+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent',root+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent']
        before={'rows':{'literal':[]},'configuration':{},'trees':{root:{n:{'metadata':[1,2,0,0,stat.S_IFDIR|0o700,2,8,1,1],'sha256':'literal'}for n in names}}}
        writes=[]
        with tempfile.TemporaryDirectory(prefix='pg783-gate-')as directory:
            temp=Path(directory);(temp/'snapshot-before.private.json').write_text(json.dumps(before))
            class Root:
                def is_dir(self):return True
                def is_symlink(self):return False
                def stat(self):return types.SimpleNamespace(st_uid=0,st_gid=0,st_mode=stat.S_IFDIR|0o700)
                def __truediv__(self,name):return temp/name
            class Epoch:
                def read_bytes(self):return b'independent INVALID literal'
            with patch.multiple(mod,ROOT=Root(),load_definitions=lambda:None,parent=lambda:None,holder=lambda:(7,11),snapshot=lambda:copy.deepcopy(before),show=lambda u:{'MainPID':'0','ControlPID':'0','Job':''},kernel_empty=lambda u:None,epoch_value=lambda raw,invalid:raw==b'independent INVALID literal'and invalid,save=lambda n,v:writes.append(n),pathlib=types.SimpleNamespace(Path=lambda p:Epoch()if p==root+'/epoch.current'else Path(p))),patch.object(os,'geteuid',lambda:0),patch.object(sys,'argv',['literal','retirement']):
                for _ in range(10):mod.main()
                self.assertEqual([],writes)
                after=copy.deepcopy(before)
                for n in names[2:]:after['trees'][root].pop(n)
                with patch.object(mod,'snapshot',lambda:copy.deepcopy(after)),patch.object(sys,'argv',['literal','retired']):mod.main()
                self.assertEqual(['retired.private.json'],writes)
                with patch.object(mod,'snapshot',lambda:{'rows':{},'configuration':{},'trees':{root:{}}}),self.assertRaises(ValueError):mod.main()
        self.assertNotIn('files.revoke(',java());self.assertNotIn('helper("stop:',java())
        ast.parse(helper())


if __name__=='__main__':unittest.main()
