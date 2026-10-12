"""Execute actual composed data functions; never only inspect printed declarations."""
import ast
import copy
import hashlib
import json
import types
import unittest
from pg1553_pending_publication_refs import source
from pg1553_pending_publication_java import java

class SourceTest(unittest.TestCase):
    def test_embedded_oracle_real_bootstrap_with_fixed_file(self):
        tree=ast.parse(source());ns={'types':types}
        constants=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='EMBED_PG1551'for x in n.targets)]
        self.assertEqual(len(constants),1);exec(compile(ast.Module(body=constants,type_ignores=[]),'<embedded independent oracle>','exec'),ns)
        m=types.ModuleType('fixture-publication');m.__file__='/var/lib/pgpt-s1-preservation/pg1553-pending-publication-tools-v1/pg1551_pending_publication_contract.py'
        exec(ns['EMBED_PG1551'],m.__dict__)
        self.assertEqual(m.PHASES,('before','approval','link-staged','exchanged','old-linked-private','release'))
        self.assertNotIn('epoch',m.PHASES)

    def test_generated_snapshot_uses_fixed_old_and_new_source_only(self):
        s=source();tree=ast.parse(s);snap=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot');v=ast.unparse(snap)
        self.assertIn("'manifestSha256': selected_bom",v);self.assertIn("'source': selected_source",v)
        self.assertIn("data['source']['commit'] == selected_source",v)
        self.assertIn("publication_phase in ['old-linked-private', 'release']",v)
        self.assertIn('publication_capture(h,contract,oracle',s)
        self.assertIn("phase_observe('link-staged')",s);self.assertIn("phase_observe('exchanged')",s)
        j=java()
        for banned in ['.invalidate(','.revoke(','freezeCandidate()','UUID.randomUUID','StartUnit','StopUnit','daemon-reload']:
            self.assertNotIn(banned,j)
        self.assertIn('Arrays.equals(Files.readAllBytes(epoch),oldEpoch)',j)

    def test_actual_inventory_check_never_rebases_after_before(self):
        node=next(n for n in ast.parse(source()).body if isinstance(n,ast.FunctionDef)and n.name=='inventory_check')
        calls=[];h=types.SimpleNamespace(capture=lambda:calls.append('before-real-capture'))
        def require(v):
            if not v:raise ValueError('fixed owner rejected')
        env={'require':require,'held':[h],'public_before':None,'actor':lambda:{'fixed':'owner'},'fixed_parent':{'fixed':'owner'}}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual composed inventory function>','exec'),env);env['inventory_check']();self.assertEqual(calls,['before-real-capture'])
        env.update(public_before={'fixed':'before'},public_actual={'fixed':'after'},publication_phase='approval',begin_ns=10,contract='fixed-crypto',oracle='fixed-oracle',time=types.SimpleNamespace(time_ns=lambda:20))
        env['publication_capture']=lambda *a:calls.append(a)
        env['inventory_check']();self.assertEqual(calls[-1][3:],({'fixed':'before'},{'fixed':'after'},'approval',10,20))
        env['actor']=lambda:{'foreign':'owner'}
        with self.assertRaises(ValueError):env['inventory_check']()

    def test_protected_current_preserves_all_other_fields(self):
        node=next(n for n in ast.parse(source()).body if isinstance(n,ast.FunctionDef)and n.name=='protected_current')
        original={'source':'OLD','manifestSha256':'OLD_BOM','artifacts':{'old.jar':'old'},'rows':{'table':[{'id':7}]},'runtime':{'epoch':'INVALID'},'units':{'root':'failed143'}}
        raw=b'{"artifacts":[{"path":"new.jar","sha256":"independent-golden"}]}'
        def require(v):
            if not v:raise ValueError('protected current differs')
        env={'require':require,'profile_expected':original,'publication_phase':'before','NEW_SOURCE':'NEW','NEW_BOM':hashlib.sha256(raw).hexdigest(),'pathlib':types.SimpleNamespace(Path=lambda p:types.SimpleNamespace(__truediv__=lambda p:None)),'hashlib':hashlib,'json':json}
        class FixturePath:
            def __truediv__(self,name):
                self.assert_name=name;return self
            def read_bytes(self):return raw
        fixture=FixturePath();env['pathlib']=types.SimpleNamespace(Path=lambda p:fixture)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual protected current>','exec'),env)
        env['protected_current'](copy.deepcopy(original))
        env['publication_phase']='old-linked-private'
        expected=copy.deepcopy(original);expected.update(source='NEW',manifestSha256=hashlib.sha256(raw).hexdigest(),artifacts={'new.jar':'independent-golden'})
        env['protected_current'](expected);self.assertEqual(fixture.assert_name,'RELEASE-MANIFEST.json');self.assertEqual(original['source'],'OLD')
        for key in ['rows','runtime','units']:
            wrong=copy.deepcopy(expected);wrong[key]={'foreign':'changed'}
            with self.assertRaises(ValueError):env['protected_current'](wrong)
        env['NEW_BOM']='0'*64
        with self.assertRaises(ValueError):env['protected_current'](expected)

if __name__=='__main__':unittest.main()
