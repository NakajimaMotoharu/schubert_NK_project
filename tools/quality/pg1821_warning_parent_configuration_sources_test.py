"""Actual emitted full helper read paths, independent state18/config2 schemas."""
import ast
import hashlib
import json
import unittest
from unittest.mock import Mock
from pg1821_warning_parent_configuration_sources import sources


class Configuration(unittest.TestCase):
    def fixture(self):
        return {'Id':'schubert-nk-morning-controller.service','LoadState':'loaded','ActiveState':'failed','SubState':'failed','Result':'exit-code','MainPID':'0','ControlPID':'0','Job':'','InvocationID':'b5a12ee25dc44ec49b08f5d084b4052f','ExecMainCode':'1','ExecMainStatus':'10','ExecMainStartTimestampMonotonic':'81404764713','ExecMainExitTimestampMonotonic':'83018952135','Type':'oneshot','Restart':'no','RemainAfterExit':'no','KillMode':'control-group','SendSIGKILL':'no'}

    def exercise(self,configs,state=None):
        generated=sources();raw=generated['pg1821_native_owned_stop.py'];tree=ast.parse(raw)
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['parent_configuration','parent_receipt']];self.assertEqual(2,len(nodes))
        ns={};exec(generated['pg1821_warning_parent_projection.py'],ns)
        def require(v):
            if not v:raise ValueError('guard refused')
        def unique(items):
            value={}
            for k,v in items:
                if k in value:raise ValueError('duplicate refused')
                value[k]=v
            return value
        calls=[];iterator=iter(configs)
        def command(args):
            calls.append(args)
            if args[0]=='/usr/bin/journalctl':return b'{"INVOCATION_ID":"b5a12ee25dc44ec49b08f5d084b4052f"}\n'
            self.assertEqual(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=Type,SuccessExitStatus'],args);return next(iterator)
        path=Mock();path.read_bytes.return_value=b'independent done';path.exists.return_value=False
        saved={};fields=self.fixture()if state is None else state
        ns.update({'command':command,'require':require,'unique':unique,'show':lambda _:fields,'holder':lambda:23,'completed':lambda rows,original:{'genuinePid1Failure':True,'genuinePid1StartDone':False,'genuineRootDone':True,'managerFailureRetained':True,'completionOutcome':'WARNING','endMonotonicUs':83018953880},'pathlib':Mock(Path=Mock(return_value=path)),'BOOT':'3d69f5af-6bac-46b1-a540-7591c4a79a0d','json':json,'hashlib':hashlib,'kernel_empty':lambda _:None,'save':lambda n,data:saved.__setitem__(n,data)})
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual state18/config2 parent receipt>','exec'),ns);ns['parent_receipt']();return saved,calls

    def test_real_state_schema_without_success_exit_field(self):
        self.assertEqual(18,len(self.fixture()));self.assertNotIn('SuccessExitStatus',self.fixture())
        config=b'Type=oneshot\nSuccessExitStatus=\n';saved,calls=self.exercise([config,config])
        self.assertEqual(3,len(calls));self.assertFalse(json.loads(saved['parent.normal.private'])['actualPid1JobDone'])

    def test_complete_config_and_two_read_invariance(self):
        good=b'Type=oneshot\nSuccessExitStatus=\n'
        for bad in [b'Type=oneshot\n',b'SuccessExitStatus=\n',b'Type=oneshot\nSuccessExitStatus=10\n',b'Type=simple\nSuccessExitStatus=\n',b'Type=oneshot\nType=oneshot\nSuccessExitStatus=\n',b'Type=oneshot\nSuccessExitStatus=\nExtra=\n',b'Type=oneshot\nSuccessExitStatus=']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):self.exercise([bad,good])
        with self.assertRaises(ValueError):self.exercise([good,b'Type=oneshot\nSuccessExitStatus=10\n'])
        with self.assertRaises(ValueError):self.exercise([good,good],{**self.fixture(),'Type':'simple'})


if __name__=='__main__':unittest.main()
