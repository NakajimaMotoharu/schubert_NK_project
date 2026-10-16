"""Independent candidate-payload checks; never executes its top-level guest or service operations."""
import ast
import os
from pathlib import Path
import tempfile
import types
import unittest
import copy
from pyflakes.api import check
import pg4104_failed_done_owned_dispatch as candidate


class CandidateTest(unittest.TestCase):
    def definitions(self, names, namespace):
        tree=ast.parse(candidate.payload())
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
        self.assertEqual(set(names),{n.name for n in nodes})
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual candidate definitions>','exec'),namespace)
        return namespace

    def test_exact_emitted_closure_static_and_no_entrypoint_or_normal_parent(self):
        raw=candidate.payload()
        self.assertEqual(0,check(raw,'<candidate>'))
        self.assertFalse(hasattr(candidate,'main'))
        self.assertNotIn('parent_receipt()',raw)
        self.assertFalse("file.RootFailedDoneRecovery','inspect'" in raw)
        self.assertTrue("file.RootFailedDoneRecovery',MODE]" in raw)
        self.assertIn('oldRoot143StillFailed',raw)
        # Exactly one systemctl stop call; never any service start/kill/reload.
        calls=[]
        for node in ast.walk(ast.parse(raw)):
            if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=='run'and node.args:
                if isinstance(node.args[0],ast.List):
                    words=[n.value for n in node.args[0].elts if isinstance(n,ast.Constant)]
                    if words[:1]==['/usr/bin/systemctl']:calls.append(words)
        self.assertEqual([['/usr/bin/systemctl','stop']],calls)

    def test_real_fd_durable_reservation_is_new_only_and_complete(self):
        def require(v):
            if not v:raise ValueError('fixture')
        with tempfile.TemporaryDirectory()as directory:
            scope=self.definitions({'durable_save'},{'require':require,'os':os,'save':Path(directory)})
            scope['durable_save']('one.private',b'fixed independent record\n')
            path=Path(directory)/'one.private'
            self.assertEqual(b'fixed independent record\n',path.read_bytes())
            self.assertEqual(0o600,path.stat().st_mode&0o777)
            with self.assertRaises(FileExistsError):scope['durable_save']('one.private',b'not replayed')
            self.assertEqual(b'fixed independent record\n',path.read_bytes())
            for name,data in [('../escape',b'x'),(None,b'x'),('empty',b''),('foreign',None)]:
                with self.assertRaises(ValueError):scope['durable_save'](name,data)

    def test_normal_completion_requires_new_child_and_scope_proofs(self):
        raw=candidate.payload()
        for required in ['child.returncode==0','RECOVERY_NORMAL_RETURN oldParentNormal=false',
                         "checked(held=False,revoked=MODE=='recover')",'manager.UnrefUnit(unit)',
                         "native_contract['destination']", "native_contract['preserved']",
                         'all-six-normal.private','independentPostRequired','recovery.plan.revoke()']:
            self.assertIn(required,raw)
        # The pre-start failure path has no child and raises; once acquired, uncertain state retains.
        self.assertIn('if child is not None:retain()',raw)

    def test_holder_rejects_recycled_or_foreign_process_before_external_action(self):
        def require(v):
            if not v:raise ValueError('fixture')
        class FakePath:
            def __truediv__(self,unused):return self
            def read_bytes(self):return b'foreign argv\0'
        ns=self.definitions({'holder'},{'require':require,'child':types.SimpleNamespace(poll=lambda:None),
             'owned':(42,77),'Path':lambda unused:FakePath(),'holder_args':b'exact pinned argv\0','holder_ticks':123})
        with self.assertRaises(ValueError):ns['holder']()
        ns['child']=types.SimpleNamespace(poll=lambda:0)
        with self.assertRaises(ValueError):ns['holder']()

    def test_actual_checked_requires_both_snapshots_peer_identity_parent_values_and_source(self):
        def require(v):
            if not v:raise ValueError('fixture')
        base={'database':{'peers':[{'pid':27,'user':'fixture','state':'active'}]}}
        for changed in [False,True]:
            calls=[];values=[copy.deepcopy(base),copy.deepcopy(base)]
            values[1]['database']['peers'][0]['state']='idle in transaction'
            if changed:values[1]['database']['peers'][0]['pid']=28
            ns=self.definitions({'checked'},{'require':require,'snapshot':lambda:values.pop(0),
                'same_values':lambda a,b:calls.append('stable-values'),
                'peer_check':lambda value,held:calls.append(('peer',held)),
                'fail_parent':lambda value:calls.append('failed-parent'),
                'preserved':lambda value,revoked:calls.append(('preserved',revoked)),
                'source_fixed':lambda:calls.append('source'),'baseline':{}})
            if changed:
                with self.assertRaises(ValueError):ns['checked']()
                self.assertEqual(['stable-values'],calls)
            else:
                self.assertEqual('idle in transaction',ns['checked']()['database']['peers'][0]['state'])
                self.assertEqual(['stable-values',('peer',True),('peer',True),'failed-parent',('preserved',False),'source'],calls)

    def test_actual_stop_reauthenticates_exact_current_capture_and_holder_before_single_fixed_command(self):
        def require(v):
            if not v:raise ValueError('fixture')
        for state,owner,code in [('changed',True,0),('same',False,0),('same',True,9),('same',True,0)]:
            calls=[]
            def holder():
                calls.append('holder');require(owner)
            def run(args,**kwargs):
                calls.append((args,kwargs['timeout']));return types.SimpleNamespace(returncode=code)
            node=next(n for n in ast.walk(ast.parse(candidate.payload()))if isinstance(n,ast.FunctionDef)and n.name=='stop')
            ns={'require':require,'captures':{'caddy.service':'same'},'show_terminal':lambda unused:state,
                'holder':holder,'subprocess':types.SimpleNamespace(run=run,DEVNULL='devnull')}
            exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual stop boundary>','exec'),ns)
            if state=='same'and owner and code==0:ns['stop']('caddy.service')
            else:
                with self.assertRaises(ValueError):ns['stop']('caddy.service')
            commands=[call for call in calls if isinstance(call,tuple)]
            self.assertEqual(([(['/usr/bin/systemctl','stop','caddy.service'],120)]if state=='same'and owner else[]),commands)

    def test_frozen_common_terminal_and_plan_modules_have_complete_static_closure(self):
        from pg4088_failed_done_owned_sources import files
        for name,text in files().items():
            if name.endswith('.py'):
                with self.subTest(file=name):self.assertEqual(0,check(text,name))

    def test_actual_source_fixed_runs_full_signed_verifier_each_phase_and_propagates_refusal(self):
        def require(v):
            if not v:raise ValueError('fixture')
        records=[{'path':'file'+str(i),'size':1,'sha256':'a'*64}for i in range(187)]
        for valid in [True,False,None,1]:
            calls=[]
            def verify(root,rows,manifest,materials):
                self.assertEqual(('/release',records,b'fixed manifest',['pin','signature']),(root,rows,manifest,materials))
                calls.append('signed187');return valid
            ns=self.definitions({'source_fixed'},{'require':require,'manifest':types.SimpleNamespace(read_bytes=lambda:b'fixed manifest'),
                'raw':b'fixed manifest','current':types.SimpleNamespace(resolve=lambda strict:'/release'),'root':'/release',
                'Path':lambda unused:types.SimpleNamespace(read_text=lambda:'fixed boot'),'boot':'fixed boot',
                'signed_contract':{'verify':verify},'data':{'artifacts':records},'fixed_materials':['pin','signature'],
                'old':{'unitFilesActual':{}},'config':lambda:calls.append('config')or {'fixed':1},'fixed_config':{'fixed':1}})
            if valid is True:
                ns['source_fixed']();ns['source_fixed']();self.assertEqual(['signed187','config']*2,calls)
            else:
                with self.assertRaises(ValueError):ns['source_fixed']()
                self.assertEqual(['signed187'],calls)


if __name__=='__main__':unittest.main()
