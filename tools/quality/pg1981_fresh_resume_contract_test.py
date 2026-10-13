"""Independent literal config/runtime/native vectors, not expected via production methods."""
import copy
import hashlib
import types
import unittest
from pg1981_fresh_resume_contract import configuration,runtime_tree
from pg1980_fresh_completed_resume_sources import sources
from pyflakes.api import check

M='schubert-nk-morning-controller.service'
D='/run/systemd/system/'+M+'.d'
TARGET=D+'/zz-pg1980-once-resume.conf'
RUN='4148e3e8-f107-431a-ab27-d6e6d1f1772e'


class Contract(unittest.TestCase):
    def test_configuration_only_canonical_two_argument_and_two_fields(self):
        old={f'fixed{i}':'literal'for i in range(30)};old.update(ExecStart='original',DropInPaths='/etc/native.conf')
        new={**old,'ExecStart':'resume','DropInPaths':'/etc/native.conf '+TARGET}
        vectors={'original':('/usr/bin/java','--literal',False,'date1','date2','42','exited','10'),'resume':('/usr/bin/java','--literal --resume '+RUN,False,'n/a','n/a','0','(null)','0/0')}
        parse=vectors.get
        expected={M:old,'ordinary':{'exact':'fixed'}};actual={M:new,'ordinary':{'exact':'fixed'}}
        ordinary=lambda a,b,unused:a==b
        self.assertTrue(configuration(expected,actual,parse,ordinary))
        for key in old:
            if key not in ['ExecStart','DropInPaths']:
                self.assertFalse(configuration(expected,{**actual,M:{**new,key:'changed'}},parse,ordinary))
        for index in range(8):
            v=list(vectors['resume']);v[index]='unknown';vectors['negative']=tuple(v)
            self.assertFalse(configuration(expected,{**actual,M:{**new,'ExecStart':'negative'}},parse,ordinary))
        for invalid in ['', '/etc/native.conf '+TARGET+' /foreign.conf',TARGET]:
            self.assertFalse(configuration(expected,{**actual,M:{**new,'DropInPaths':invalid}},parse,ordinary))
        for invalid in [None,{}, {**actual,'foreign':{}}, {M:{**new,'fixed0':None},'ordinary':{'exact':'fixed'}}, {M:new,'ordinary':{'exact':'changed'}}]:
            self.assertFalse(configuration(expected,invalid,parse,ordinary))
        self.assertFalse(configuration({}, {},parse,ordinary))

    def test_runtime_exact_namespace_and_all_inode_fields(self):
        drop=b'[Service]\n';root={'metadata':[28,3,0,0,16877,3,60,1,1],'sha256':None}
        before={'/run/systemd/system':root,D:{'metadata':[28,5514,0,0,16877,2,40,10,10],'sha256':None}}
        after={'/run/systemd/system':copy.deepcopy(root),D:{'metadata':[28,5514,0,0,16877,2,80,20,20],'sha256':None},TARGET:{'metadata':[28,9900,0,0,33188,1,len(drop),20,20],'sha256':hashlib.sha256(drop).hexdigest()}}
        self.assertTrue(runtime_tree(before,after,drop,15,25))
        for index in range(9):
            for path in ['/run/systemd/system',D,TARGET]:
                invalid=copy.deepcopy(after);invalid[path]['metadata'][index]+=100
                if path==D and index==6:
                    invalid[path]['metadata'][index]=39
                if path==TARGET and index==1:
                    invalid[path]['metadata'][index]=5514
                self.assertFalse(runtime_tree(before,invalid,drop,15,25))
        for invalid in [None,{}, {**after,'foreign':root}, {k:v for k,v in after.items()if k!=TARGET}]:
            self.assertFalse(runtime_tree(before,invalid,drop,15,25))
        invalid=copy.deepcopy(after);invalid[TARGET]['sha256']='0'*64
        self.assertFalse(runtime_tree(before,invalid,drop,15,25))
        self.assertFalse(runtime_tree(before,after,b'',15,25));self.assertFalse(runtime_tree(before,after,drop,26,25))
        self.assertFalse(runtime_tree(before,after,drop,None,25))

    def test_actual_emitted_writer_full_golden_and_prepared_scope_static(self):
        s=sources();self.assertEqual(20,len(s))
        for name,raw in s.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual '+name+'>'))
        module=types.ModuleType('actual_new_writer');exec(compile(s['pg1980_runtime_writer.py'],'<actual finite writer>','exec'),module.__dict__)
        base=b'ExecStart=/usr/bin/java -cp /opt/nk.jar dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
        argv=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp /opt/nk.jar dev.codex.schubert.nk.batch.file.MorningProcessMain'
        native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
        expected=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume 4148e3e8-f107-431a-ab27-d6e6d1f1772e\n'
        self.assertEqual(expected,module.fixed_dropin(base,native))
        self.assertEqual('zz-pg1980-once-resume.conf',module.NAME);self.assertEqual(RUN,module.RUN_ID)
        for badbase,badnative in [(None,native),(base,None),(base.replace(b'ExecStart=',b'Other='),native),(base,native+b'foreign\n')]:
            with self.assertRaises(ValueError):module.fixed_dropin(badbase,badnative)
        refs=s['pg1980_native_refs.py'];java=s['Pg1980FreshResumePreparation.java']
        self.assertIn("'SuccessExitStatus': '10'",refs);self.assertNotIn('existing_unit',refs)
        self.assertIn('pg1963-reload-ref-scoped-full-post-v1',refs);self.assertIn('normalSingleRuntimeReload=true',java)
        self.assertIn('4148e3e8-f107-431a-ab27-d6e6d1f1772e',java)
        self.assertNotIn('only_normal_reload',refs.lower())


if __name__=='__main__':unittest.main()
