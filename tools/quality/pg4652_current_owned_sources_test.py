"""Current full15/actual dispatch closure and immutable output bounds; never stop authority."""
import ast
import builtins
import inspect
import symtable
import unittest
from collections import Counter
from pyflakes.api import check,checkPath
import pg4652_current_owned_sources as role
import pg4656_current_owned_dispatch as dispatch
import pg4658_current_owned_post as post
from immutable_payload_binding import PROTECTED


def fixture():
    b=role.admission.live();binding={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
    state={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','Result':'success','SuccessExitStatus':'10','ExecMainCode':'0','InvocationID':'','ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0','ExecMainStatus':'0'}
    fields={k:v for k,v in state.items()if k!='SuccessExitStatus'};fields.update(Id='schubert-nk-morning-controller.service',LoadState='loaded',Type='oneshot',Restart='no',RemainAfterExit='no',KillMode='control-group',SendSIGKILL='no')
    ctx=role.context();return ctx,binding,state,fields


def capsules(raw):return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


class CurrentOwned(unittest.TestCase):
    def test_all_fifteen_current_outputs_and_capsule_preservation(self):
        args=fixture();result=role.emit(*args)
        self.assertEqual(15,len(result));self.assertEqual(4,sum(n.endswith('.java')for n in result));self.assertEqual(11,sum(n.endswith('.py')for n in result))
        for name,raw in result.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,name))
            self.assertNotIn(role.previous.TOOLS,raw)
        receipt=result['pg4652_parent_receipt.py'];self.assertIn('def _normal_classify',receipt);self.assertIn(args[1]['binding']['invocation'],receipt)
        sample='SOURCE='+repr(role.previous.SOURCE)+'\nROOT_ORACLE='+repr('SOURCE='+repr(role.previous.SOURCE))+'\n'
        updated=role.final_bind(sample)
        self.assertEqual(capsules(sample),capsules(updated))
        self.assertIn('SOURCE='+repr(role.SOURCE),updated)
        self.assertEqual('a'+role.previous.SOURCE+'b'*23,role.role_text('a'+role.previous.SOURCE+'b'*23))

    def test_independent_post_complete_seals_and_namespace(self):
        import pg1257_fresh_independent_terminal_post as old
        ctx,live,_,_=fixture();ns=post.namespace()
        with self.assertRaises(ValueError):ns['emit']({},ctx,live)
        raw=ns['emit']({n:'a'*64 for n in old.previous.SEALS},ctx,live)
        self.assertEqual(0,check('HASHES={}\nRECEIPT="fixture"\n'+raw,'<current full independent post>'))
        self.assertIn(post.SLOT,raw);self.assertIn(role.composite.SLOT,raw)

    def test_actual_dispatch_runtime_globals_and_fresh_output(self):
        ns=dispatch.namespace();raw=ns['run_source']()
        base=dispatch.previous.previous.template.old.previous
        constructor=role.bind(inspect.getsource(base.run_action));tree=ast.parse(constructor);fn=tree.body[0]
        self.assertEqual(4,len(fn.body));self.assertIsInstance(fn.body[0],ast.Assign);self.assertIsInstance(fn.body[1],ast.Assign)
        fn.body=fn.body[:2]+[ast.Return(value=ast.Name(id='ns',ctx=ast.Load()))];ast.fix_missing_locations(tree)
        local={**ns['run_action'].__globals__};exec(compile(tree,'<actual constructor without operation>','exec'),local)
        runtime=local['run_action']('NO_OPERATION');exec(compile(raw,'<actual current dispatch declarations>','exec'),runtime)
        function=next(c for c in symtable.symtable(raw,'<actual current dispatch>','exec').get_children()if c.get_name()=='run_action')
        missing=[s.get_name()for s in function.get_symbols()if s.is_global()and s.is_referenced()and s.get_name()not in runtime and not hasattr(builtins,s.get_name())]
        self.assertEqual([],missing)
        self.assertIn("post = {**post['result'], 'actualExit':post['actualExit'], 'productionSource':post['source']}",raw)
        self.assertIn('pg4654-frozen-v1.safe.json',raw);self.assertIn('pg4659-newboot-pre-stop-full-v1',raw)
        fresh=dispatch.rename_output(ns['post_payload'](),role.composite.SLOT,'pg4659-newboot-pre-stop-full-v1')
        self.assertIn("SAVE = BASE / 'pg4659-newboot-pre-stop-full-v1'",fresh)
        self.assertIn("save=SAVE",fresh);self.assertIn('originalCompositeReplayed',fresh)
        self.assertEqual(0,check(fresh,'<small same-source fresh pre-stop current certificate>'))
        self.assertEqual(capsules(ns['post_payload']()),capsules(fresh))

    def test_output_rename_rejects_history_or_foreign_definition(self):
        raw="SAVE=BASE/'old'\nCHAIN={'history':"+repr(role.composite.SLOT)+"}\nSAVE=BASE/"+repr(role.composite.SLOT)+";require(not exists(SAVE))\n"
        updated=dispatch.rename_output(raw,role.composite.SLOT,'new-only')
        self.assertEqual(capsules(raw),capsules(updated))
        for bad in ['CHAIN={}\n',"SAVE=OTHER/'foreign'","SAVE=BASE/'foreign'",'SAVE=call()']:
            with self.assertRaises(ValueError):dispatch.rename_output(bad,role.composite.SLOT,'new-only')
        for name in ['pg4650_current_parent_projection.py','pg4652_current_owned_sources.py','pg4654_current_owned_compile.py','pg4656_current_owned_dispatch.py','pg4658_current_owned_post.py','pg4652_current_owned_sources_test.py']:
            self.assertEqual(0,checkPath('tools/quality/'+name))


if __name__=='__main__':unittest.main()
