"""Pure new normal graph and actual dispatcher namespace, no authority execution."""
import ast
import unittest
from pyflakes.api import check,checkPath
from pg4752_new_current_admission_test import NewAdmission
import pg4772_new_current_owned_sources as role
import pg4776_new_current_owned_dispatch as dispatch
import pg4778_new_current_owned_post as post
from immutable_payload_binding import PROTECTED


class NormalOwned(unittest.TestCase):
    def fixture(self):
        b=NewAdmission().binding();live={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
        state={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','Result':'success','SuccessExitStatus':'10','ExecMainCode':'1','InvocationID':b['invocation'],'ExecMainStartTimestampMonotonic':str(b['start']),'ExecMainExitTimestampMonotonic':str(b['start']+1000000),'ExecMainStatus':'10'}
        fields={k:v for k,v in state.items()if k!='SuccessExitStatus'};fields.update(Id='schubert-nk-morning-controller.service',LoadState='loaded',Type='oneshot',Restart='no',RemainAfterExit='no',KillMode='control-group',SendSIGKILL='no')
        owned={u:[str(10000+i),c*32,2000+i,'a'*64]for i,(u,c)in enumerate(zip(['artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service'],'bcde'))}
        return ('d'*64,owned,{'endMonotonicUs':b['start']+1000000},'2026-10-16T22:12:39Z'),live,state,fields

    def test_complete_new_graph_static_and_protected_capsules(self):
        args=self.fixture();original=role.namespace()['emit'](*args);actual=role.emit(*args)
        self.assertEqual({'Pg4772NativeArgumentTest.java','Pg4772NativeStop.java','Pg4772OriginalTupleTest.java','Pg4772StopLabelTest.java',*{'pg4772_'+n+'.py'for n in ['configuration','configuration_capture','durable','native_owned_stop','native_refs','parent_receipt','row_bound','stable_journal','warning_parent_projection']},'pg526_native_term_witness.py','pg526_term_witness.py'},set(actual))
        def capsules(raw):
            return [ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets)]
        for name,raw in original.items():
            output=actual[role.final_bind(name)]
            if name.endswith('.py'):
                self.assertEqual(0,check(output,'<new normal owned>'))
                self.assertEqual(capsules(raw),capsules(output))
            self.assertNotIn(role.previous.TOOLS,output)
        self.assertIn('def _normal_classify',actual['pg4772_parent_receipt.py'])

    def test_new_dispatch_and_post_no_old_output_or_new_authority(self):
        ns=dispatch.namespace();raw=ns['run_source']()
        self.assertIn('pg4774-frozen-v1.safe.json',raw);self.assertNotIn('pg4284-frozen-v1.safe.json',raw)
        self.assertIn('pg4776-',raw)
        self.assertIn('emit',post.namespace())
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(dispatch.__file__))


if __name__=='__main__':unittest.main()
