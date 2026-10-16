"""Pure actual graph generation/closure; fixture completion never permits a stop."""
import ast
import builtins
import inspect
import symtable
import unittest
from collections import Counter
from pyflakes.api import check
import pg4282_current_owned_sources as role
import pg4286_current_owned_dispatch as dispatch
import pg4288_current_owned_post as post
from immutable_payload_binding import PROTECTED


def fixture():
    b=role.live();live={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
    state={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','Result':'success','SuccessExitStatus':'10',
      'ExecMainCode':'1','InvocationID':b['invocation'],'ExecMainStartTimestampMonotonic':str(b['start']),
      'ExecMainExitTimestampMonotonic':str(b['start']+1000000),'ExecMainStatus':'10'}
    fields={k:v for k,v in state.items()if k!='SuccessExitStatus'}
    fields.update(Id='schubert-nk-morning-controller.service',LoadState='loaded',Type='oneshot',Restart='no',RemainAfterExit='no',KillMode='control-group',SendSIGKILL='no')
    owned={u:[str(10000+i),c*32,2000+i,'a'*64]for i,(u,c)in enumerate(zip(['artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service'],'bcde'))}
    return ('d'*64,owned,{'endMonotonicUs':b['start']+1000000},'2026-10-16T11:32:54Z'),live,state,fields


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


class CurrentOwned(unittest.TestCase):
    def test_independent_post_full_namespace_and_complete_seals_required(self):
        import pg1257_fresh_independent_terminal_post as old
        ctx,live,_,_=fixture();ns=post.namespace()
        with self.assertRaises(ValueError):ns['emit']({},ctx,live)
        raw=ns['emit']({n:'a'*64 for n in old.previous.SEALS},ctx,live)
        self.assertEqual(check('HASHES={}\nRECEIPT="fixture"\n'+raw,'<complete independent current post>'),0)
        self.assertIn(post.SLOT,raw);self.assertIn(role.composite.SLOT,raw)
        self.assertNotIn('pg4048-literal-invariant-owned-post-v1',raw)

    def test_all15_emit_whole_python_and_preserve_capsules(self):
        args=fixture();ns=role.previous.namespace();ns['terminal_payload']=role.acceptance.terminal_payload
        original=ns['emit'](*args);result=role.emit(*args)
        self.assertEqual(len(result),15);self.assertEqual(sum(n.endswith('.java')for n in result),4)
        self.assertEqual(sum(n.endswith('.py')for n in result),11)
        for name,raw in original.items():
            first=role.previous.final_bind(raw);final=result[role.final_bind(name)]
            if name.endswith('.py'):
                self.assertEqual(check(final,'<whole current owned '+name+'>'),0)
                self.assertEqual(capsules(first),capsules(final))
            self.assertNotIn(role.previous.TOOLS,final)
        receipt=result['pg4282_parent_receipt.py']
        self.assertIn(args[1]['binding']['invocation'],receipt)
        self.assertIn('def _normal_classify',receipt)

    def test_dispatch_complete_real_runtime_namespace_and_explicit_unwrap(self):
        ns=dispatch.namespace();raw=ns['run_source']()
        # Capture only the actual function's pure namespace constructor. Never
        # evaluate its following exec or run_action(action) operational entry.
        raw_constructor=role.bind(inspect.getsource(dispatch.previous.template.old.previous.run_action))
        compiled={};exec(compile(raw_constructor,'<same constructor only definition>','exec'),compiled)
        self.assertEqual(compiled['run_action'].__code__.co_code,ns['run_action'].__code__.co_code)
        self.assertEqual(compiled['run_action'].__code__.co_consts,ns['run_action'].__code__.co_consts)
        tree=ast.parse(raw_constructor);fn=tree.body[0]
        self.assertEqual(len(fn.body),4)
        self.assertIsInstance(fn.body[0],ast.Assign);self.assertIsInstance(fn.body[1],ast.Assign)
        fn.body=fn.body[:2]+[ast.Return(value=ast.Name(id='ns',ctx=ast.Load()))]
        ast.fix_missing_locations(tree);local={**ns['run_action'].__globals__}
        exec(compile(tree,'<pure actual namespace constructor>','exec'),local)
        runtime=local['run_action']('NO_OPERATION')
        function=symtable.symtable(raw,'<actual dispatch>','exec').get_children()[0]
        missing=[s.get_name()for s in function.get_symbols()if s.is_global()and s.is_referenced()and s.get_name()not in runtime and not hasattr(builtins,s.get_name())]
        self.assertEqual(missing,[])
        self.assertIn("post = {**post['result'], 'actualExit':post['actualExit'], 'productionSource':post['source']}",raw)
        self.assertIn('pg4284-frozen-v1.safe.json',raw)
        self.assertIn('pg4286-',raw)
        self.assertNotIn('pg4046-',raw)


if __name__=='__main__':unittest.main()
