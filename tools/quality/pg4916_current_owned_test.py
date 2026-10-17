import ast
import builtins
from collections import Counter
import datetime
import inspect
import symtable
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from immutable_payload_binding import PROTECTED
import pg4916_current_owned_sources as role
import pg4920_current_owned_dispatch as dispatch
import pg4922_current_owned_post as post
import pg2556_strict_current_owned_dispatch as constructor_source


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in PROTECTED for t in n.targets))


class Owned(unittest.TestCase):
    def fixture(self):
        # Source-emission-only golden: not an actual completed Root receipt.
        b=role.admission.live();live={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
        state={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','Result':'success','SuccessExitStatus':'10','ExecMainCode':'1','InvocationID':b['invocation'],'ExecMainStartTimestampMonotonic':str(b['start']),'ExecMainExitTimestampMonotonic':str(b['start']+1000000),'ExecMainStatus':'10'}
        fields={k:v for k,v in state.items()if k!='SuccessExitStatus'};fields.update(Id='schubert-nk-morning-controller.service',LoadState='loaded',Type='oneshot',Restart='no',RemainAfterExit='no',KillMode='control-group',SendSIGKILL='no')
        owned={u:[str(10000+i),c*32,2000+i,'a'*64] for i,(u,c)in enumerate(zip(('artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service'),'bcde'))}
        ended=(datetime.datetime.fromisoformat(b['cutoff'].replace('Z','+00:00'))+datetime.timedelta(seconds=1)).isoformat()
        return ('d'*64,owned,{'endMonotonicUs':b['start']+1000000},ended),live,state,fields

    def test_complete_emitted_owned_graph_preserves_every_protected_capsule(self):
        args=self.fixture();original=role.namespace()['emit'](*args);values=role.emit(*args)
        expected={'Pg4916NativeArgumentTest.java','Pg4916NativeStop.java','Pg4916OriginalTupleTest.java','Pg4916StopLabelTest.java',*{'pg4916_'+n+'.py'for n in ('configuration','configuration_capture','durable','native_owned_stop','native_refs','parent_receipt','row_bound','stable_journal','warning_parent_projection')},'pg526_native_term_witness.py','pg526_term_witness.py'}
        self.assertEqual(expected,set(values))
        for name,raw in original.items():
            actual=values[role.final_bind(name)]
            if name.endswith('.py'):self.assertEqual(0,check(actual,'<whole current owned>'));self.assertEqual(capsules(raw),capsules(actual))
            self.assertNotIn(role.previous.TOOLS,actual)
        self.assertIn('def _normal_classify',values['pg4916_parent_receipt.py'])

    def test_both_output_paths_are_fresh_and_protected_data_never_rewritten(self):
        raw="CHAIN={'history':'old-raw'}\nORACLE='old-raw literal'\nGUARD='old-raw literal'\nRAW_SAVE=BASE/'old-raw';require(not exists(RAW_SAVE))\nSAVE=BASE/'old';require(not exists(SAVE))\n"
        actual=dispatch.rename_output(raw,'old','fresh')
        self.assertIn("RAW_SAVE=BASE/'fresh-raw'",actual);self.assertIn("SAVE=BASE/'fresh'",actual)
        self.assertEqual(capsules(raw),capsules(actual))
        for bad in (raw.replace("BASE/'old-raw'","BASE/'foreign'"),raw.replace('RAW_SAVE=','OTHER='),raw+"RAW_SAVE=BASE/'old-raw'\n"):
            with self.assertRaises(ValueError):dispatch.rename_output(bad,'old','fresh')

    def test_actual_full_composite_renames_both_outputs_without_touching_nested_oracles(self):
        original=role.composite.root.payload(role.admission.live(),'a'*64)
        composed=role.composite.compose(original,{'before':{},'after':{},'context':{'fixtureOnly':True}},'b'*64)
        actual=dispatch.rename_output(composed,role.composite.SLOT,'pg4923-newboot-pre-stop-full-v1')
        self.assertEqual(capsules(composed),capsules(actual));self.assertEqual(0,check(actual,'<actual whole pre-stop full composite>'))
        values={n.targets[0].id:ast.literal_eval(n.value.right)for n in ast.parse(actual).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in {'SAVE','RAW_SAVE'}}
        self.assertEqual({'SAVE':'pg4923-newboot-pre-stop-full-v1','RAW_SAVE':'pg4923-newboot-pre-stop-full-v1-raw'},values)
        self.assertIn("SAVE = BASE / 'pg1562-pending-runtime-v1'",actual)
        with self.assertRaises(ValueError):dispatch.rename_output(composed.replace('pg1562-pending-runtime-v1','foreign-default'),role.composite.SLOT,'pg4923-newboot-pre-stop-full-v1')

    def test_actual_dispatch_namespace_complete_and_first_stop_selector(self):
        ns=dispatch.namespace();raw=ns['run_source']()
        for text in ('pg4918-frozen-v1.safe.json','pg4920-','pg4923-newboot-pre-stop-full-v1',"post['result']"):
            self.assertIn(text,raw)
        self.assertNotIn('pg4776-',raw);self.assertIn('RAW_SAVE',raw)
        function=next(c for c in symtable.symtable(raw,'<actual stage/stop>','exec').get_children() if c.get_name()=='run_action')
        # These are runtime-constructor globals; inspect the actual deferred
        # constructor without executing a stage/stop or fabricating a receipt.
        constructor=ns['run_action'];self.assertIn('exec',constructor.__code__.co_names)
        source=role.bind(inspect.getsource(constructor_source.run_action));env={**constructor.__globals__}
        exec(compile(source,'<actual deferred constructor>','exec'),env)
        self.assertEqual(constructor.__code__.co_code,env['run_action'].__code__.co_code)
        self.assertEqual(constructor.__code__.co_consts,env['run_action'].__code__.co_consts)
        tree=ast.parse(source);fn=tree.body[0];self.assertEqual(4,len(fn.body))
        fn.body=fn.body[:2]+[ast.Return(value=ast.Name(id='ns',ctx=ast.Load()))]
        exec(compile(ast.fix_missing_locations(tree),'<pure constructor only, no action>','exec'),env)
        runtime=env['run_action']('NO_OPERATION');exec(compile(raw,'<actual first-stop complete globals>','exec'),runtime)
        missing=[s.get_name()for s in function.get_symbols()if s.is_global()and s.is_referenced()and s.get_name()not in runtime and not hasattr(builtins,s.get_name())]
        self.assertEqual([],missing);self.assertEqual(role.SOURCE,runtime['SOURCE'])
        with self.assertRaisesRegex(ValueError,'fixed action'):runtime['run_action']('INVALID_ACTION')
        actual=post.namespace()['entry']();strings={v for v in actual.__code__.co_consts if isinstance(v,str)}
        self.assertIn('pg4920-stop-v1.safe.json',strings);self.assertNotIn('pg4806-stop-v1.safe.json',strings)
        self.assertIn('pg4918-frozen-v1.safe.json',strings);self.assertEqual(role.SOURCE,actual.__globals__['SOURCE'])
        self.assertNotIn('run_action',actual.__code__.co_names)
        for path in (role.__file__,dispatch.__file__,post.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_failed_stop_receipt_cannot_issue_independent_guest_read(self):
        from pathlib import Path
        actual=post.namespace()['entry']()
        with patch.object(actual.__globals__['subprocess'],'check_output',return_value=b''),patch.object(Path,'read_bytes',return_value=b'{"actualExit":1,"sourceQualified":false,"productionSource":"04bbdb73b532537e3546191d72dee913b17629a0"}'),patch.object(actual.__globals__['subprocess'],'run')as execute:
            with self.assertRaises(ValueError):actual()
            execute.assert_not_called()


if __name__=='__main__':unittest.main()
