"""Independent owner/terminal and spawn-race tests for actual emitted functions."""
import ast
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4510_metadata_only_handoff_sources as s
import pg4512_metadata_only_stage as stage


class MetadataOnly(unittest.TestCase):
    def fixture(self):
        owner={'pid':828676,'ticks':16705476,'argvSha256':'51c27aa637200ae1f7a30fccb7dd27511286366392131c40edf7fde823787349',
         'cgroup':'0::/user.slice/user-1000.slice/session-1042.scope\n','children':[829193],
         'authority':{'PPid':'828674','Uid':'0 0 0 0','Gid':'0 0 0 0','Groups':'0','NoNewPrivs':'0','CapInh':'0000000000000000','CapAmb':'0000000000000000','CapPrm':'000001ffffffffff','CapEff':'000001ffffffffff','CapBnd':'000001ffffffffff'},
         'fds':{str(n):{'target':target,'metadata':[28,10+n,0,0,4480 if n<3 else 49663,1,0,100,100],'fdinfo':'pos: 0\nflags: 00\n'}for n,target in enumerate(['pipe:[14183497]','pipe:[14183498]','pipe:[14183499]','socket:[14182061]'])}}
        terminal={'pid':829193,'ticks':16712075,'state':'Z','ppid':828676,'rawWaitStatus':0,'statSha256':'dd7f940c77cd271cb77d48de7f99d4a4e3d26fb69b71c65a344a7e597cc57efb'}
        return owner,terminal

    def test_exact_owner_and_full_every_field_mutation_rejected(self):
        old,t=self.fixture();self.assertTrue(s.metadata_owner(old,copy.deepcopy(old),t))
        for key in old:
            v=copy.deepcopy(old);v[key]=None
            with self.subTest(key=key),self.assertRaises(ValueError):s.metadata_owner(old,v,t)
        for fd in ['0','1','2','3']:
            for key in ['target','metadata','fdinfo']:
                v=copy.deepcopy(old);v['fds'][fd][key]=None
                with self.subTest(fd=fd,key=key),self.assertRaises(ValueError):s.metadata_owner(old,v,t)
        for key in t:
            bad=dict(t);bad[key]=None
            with self.subTest(terminal=key),self.assertRaises(ValueError):s.metadata_owner(old,old,bad)

    def test_emitted_full_static_and_only_one_metadata_term(self):
        raw=s.payload();self.assertEqual(0,check(raw,'<actual metadata controller>',Reporter(io.StringIO(),io.StringIO())))
        self.assertEqual(0,check(stage.stage_payload(),'<actual stage>',Reporter(io.StringIO(),io.StringIO())))
        calls=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([(828676,16705476)],[(n.args[0].value,n.args[1].value)for n in calls])
        self.assertNotIn('proc(child.pid)',s.BODY)

    def test_actual_post_records_fixed_start_and_wait_even_if_any_proc_census_would_fail(self):
        fn=next(n for n in ast.parse(s.payload()).body if isinstance(n,ast.FunctionDef)and n.name=='run_post')
        for code in [0,7]:
            with tempfile.TemporaryDirectory()as folder:
                records=[];events=[]
                expected={'actualExit':0,'newMARDDBTenRefNormalClose':True,'all24OriginalBackupNativeUnitConfigUnchanged':True,'oldParentNormal':False}
                def private(name,value):records.append((name,value));return 'fixture-digest'
                def require(value):
                    if value is not True:raise ValueError('post failed')
                def popen(argv,**kw):
                    events.append('spawn');self.assertEqual(['/usr/bin/python3','-B','-c','literal-payload'],argv)
                    kw['stdout'].write((json.dumps(expected)+'\n').encode())
                    return types.SimpleNamespace(pid=900001,wait=lambda:events.append('wait')or code)
                def forbidden_proc(pid):raise FileNotFoundError('intentional short-lived child FD')
                import hashlib
                ns={'private':private,'hashlib':hashlib,'POST_SOURCE':'literal-payload','os':os,'save':Path(folder),'subprocess':types.SimpleNamespace(Popen=popen,DEVNULL=-3),'proc':forbidden_proc,'require':require,'json':json}
                exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual post start/wait>','exec'),ns)
                if code==0:self.assertEqual(expected,ns['run_post']())
                else:
                    with self.assertRaises(ValueError):ns['run_post']()
                self.assertEqual(['spawn','wait'],events)
                self.assertEqual(['post-start-reservation.private.json','post-start-pid.private.json','post-exit.safe.json'],[r[0]for r in records])
                self.assertEqual(code,records[-1][1]['actualExit'])


if __name__=='__main__':unittest.main()
