"""Actual protected whole row branch and negative field/null/schema tests."""
import ast
import copy
import hashlib
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from pg1567_existing_runtime_sources import java,refs

class VerifyTest(unittest.TestCase):
    def test_actual_runtime_provider_real_fd_complete_rows(self):
        sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
        from pg1090_cold_finite_capture import direct_tree
        node=next(n for n in ast.parse(refs()).body if isinstance(n,ast.FunctionDef)and n.name=='runtime_rows')
        def require(v):
            if not v:raise ValueError('runtime provider graph refused')
        with tempfile.TemporaryDirectory(prefix='pg1567-independent-fd-')as name:
            root=Path(name);directory=root/'schubert-nk-morning-controller.service.d';directory.mkdir();target=directory/'zz-pg1160-once-resume.conf';target.write_bytes(b'independent-golden')
            env={'RUNTIME':root,'writer':types.SimpleNamespace(UNIT=directory.name,NAME=target.name),'require':require,'direct_tree':direct_tree}
            exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual complete FD row provider>','exec'),env);value=env['runtime_rows']()
            self.assertEqual(set(value),{str(root),str(directory),str(target)})
            for row in value.values():self.assertEqual(set(row),{'metadata','sha256','target','acl'});self.assertEqual(row['acl'],[])
            self.assertEqual(value[str(target)]['sha256'],hashlib.sha256(b'independent-golden').hexdigest())
            (directory/'foreign').write_bytes(b'foreign')
            with self.assertRaises(ValueError):env['runtime_rows']()

    def test_actual_whole_row_schema_not_old_tree_assumption(self):
        node=next(n for n in ast.parse(refs()).body if isinstance(n,ast.FunctionDef)and n.name=='protected_runtime')
        root='/run/systemd/system';directory=root+'/schubert-nk-morning-controller.service.d';target=directory+'/zz-pg1160-once-resume.conf';body=b'independent-literal';digest=hashlib.sha256(body).hexdigest()
        rows={root:{'metadata':[28,71,0,0,stat.S_IFDIR|0o755,3,60,10,10],'sha256':None,'target':None,'acl':[]},directory:{'metadata':[28,72,0,0,stat.S_IFDIR|0o755,2,60,10,10],'sha256':None,'target':None,'acl':[]},target:{'metadata':[28,73,0,0,stat.S_IFREG|0o644,1,len(body),10,10],'sha256':digest,'target':None,'acl':[]}}
        fixed={p:{'metadata':copy.deepcopy(v['metadata']),'sha256':v['sha256']}for p,v in rows.items()}
        before={'oneTimeRuntime':fixed,'rows':{'table':[7]},'epoch':'INVALID','unit':'oldfailed143'}
        actual={'oneTimeRuntime':copy.deepcopy(rows),'rows':{'table':[7]},'epoch':'INVALID','unit':'oldfailed143'}
        def require(v):
            if not v:raise ValueError('whole current/runtime refused')
        env={'require':require,'profile_expected':before,'RUNTIME':Path(root),'writer':types.SimpleNamespace(UNIT='schubert-nk-morning-controller.service.d',NAME='zz-pg1160-once-resume.conf'),'dropin':body,'hashlib':hashlib,'stat':stat}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual protected fullrow schema>','exec'),env);env['protected_runtime'](actual)
        with self.assertRaises(ValueError):env['protected_runtime'](None)
        for change in ['old-schema','ACL','target','inode','hash','extra','missing','row','epoch']:
            bad=copy.deepcopy(actual)
            if change=='old-schema':bad['oneTimeRuntime']=copy.deepcopy(fixed)
            elif change=='ACL':bad['oneTimeRuntime'][target]['acl']=['foreign']
            elif change=='target':bad['oneTimeRuntime'][target]['target']='foreign'
            elif change=='inode':bad['oneTimeRuntime'][target]['metadata'][1]+=1
            elif change=='hash':bad['oneTimeRuntime'][target]['sha256']='0'*64
            elif change=='extra':bad['oneTimeRuntime']['foreign']=copy.deepcopy(rows[target])
            elif change=='missing':del bad['oneTimeRuntime'][target]
            elif change=='row':bad['rows']={'foreign':8}
            else:bad['epoch']='ISSUED'
            with self.assertRaises(ValueError):env['protected_runtime'](bad)

    def test_no_reprepare_reload_root_or_epoch_and_actual_schema_provider(self):
        s=refs();j=java();ast.parse(s)
        for banned in ['runtime.owned_prepare(',"command(['/usr/bin/systemctl','daemon-reload']",'StartUnit','StopUnit','.invalidate(','.revoke(']:self.assertNotIn(banned,s+j)
        self.assertIn("'oneTimeRuntime': runtime_rows()",s);self.assertIn('child=direct_tree(directory)',s)
        self.assertIn('verify-existing',s+j);self.assertIn('978f6867d38a186ab3a18a30bbc93827f2c5318203d671ccc77119ee36b13ef2',s)

if __name__=='__main__':unittest.main()
