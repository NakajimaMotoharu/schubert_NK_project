"""Independent current ordinary generation/foreign/null and one-stop guards."""
import ast
import copy
import unittest
from pg1609_current_ordinary_owned_stop_sources import sources,BEFORE
from pg1610_current_ordinary_stop_compile import compiler_source
from pg1611_current_ordinary_owned_stop_dispatch import source,STAGE
from pg1612_current_ordinary_stop_preflight import payload as preflight
from pg1613_current_ordinary_stop_independent_post import payload as post
from pg526_term_witness import FIELDS

class OrdinaryOwnedStopTest(unittest.TestCase):
    def test_real_abi_current_tuple_and_every_live_field(self):
        values=sources();self.assertEqual(len(values),14)
        tree=ast.parse(values['pg1609_native_owned_stop.py']);names={'require','validate_live'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'EXPECTED','ORDER'}for t in n.targets)]
        env={'FIELDS':FIELDS};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual ordinary stop guard>','exec'),env)
        owned={'caddy.service':('259611','99a144b6cba34d9e8ebdbfad060302de'),'schubert-nk-web.service':('257744','7a75a61efae5403692eb523eea322c19'),'schubert-nk-api.service':('256734','994fd53232ee426d9ca93a2f311bda53'),'artemis.service':('216143','db75a3f0c2494fdea570b30012a5b871')}
        self.assertEqual(env['EXPECTED'],owned)
        self.assertEqual(env['ORDER'],['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'])
        states={u:{}for u in env['ORDER']}
        for u,(pid,inv)in owned.items():
            states[u]={k:'0'for k in FIELDS};states[u].update(MainPID=pid,InvocationID=inv,ActiveState='active',SubState='running',Job='',ControlPID='0',Result='success',Id=u,LoadState='loaded')
        env['validate_live'](states)
        for u in owned:
            for k in ['MainPID','InvocationID','ActiveState','SubState','ControlPID','Job','Result','Id','LoadState','ExecMainCode','ExecMainStatus','ExecMainExitTimestampMonotonic']:
                changed=copy.deepcopy(states);changed[u][k]='foreign'
                with self.assertRaises(ValueError):env['validate_live'](changed)
        for bad in [None,{},dict(states,foreign={})]:
            with self.assertRaises(ValueError):env['validate_live'](bad)
        java=values['Pg1609NativeStop.java'];self.assertIn('db.setReadOnly(true)',java);self.assertIn('PG1544',java)
        self.assertIn('/proc/204695',values['pg1609_native_refs.py'])
        for v in values.values():
            self.assertNotIn('c52c914a72804a89b0fd5f252f6ac0fc',v);self.assertNotIn('15700a87-9117-4f63-a0ff-768dd604d0f1',v)

    def test_current_seal_constructor_once_and_post_join(self):
        self.assertIn('Pg1609OriginalTupleTest',compiler_source())
        dispatch=source();self.assertIn("'.requested'",dispatch);self.assertIn('pg1612-current-ordinary-stop-preflight-v1.safe.json',dispatch)
        self.assertIn('pg1609-current-ordinary-owned-stop-tools-v1',STAGE)
        self.assertIn('pg1612-current-ordinary-stop-preflight-v1',preflight())
        self.assertIn('pg1608-current-observation-full-seal-v3',sources()['pg1609_native_refs.py'])
        raw=post({n:c*64 for n,c in zip(['before.private.json','after.private.json','complete.private','parent.private.jsonl'],'abcd')})
        self.assertIn(BEFORE,sources()['pg1609_native_refs.py'])
        for literal in ['39951854181','204695,256734,257744,259611,216143','d28eead2-941c-4b97-9747-1758c0809e29.done']:
            self.assertTrue(literal in raw,'missing independently captured literal: '+literal)

if __name__=='__main__':unittest.main()
